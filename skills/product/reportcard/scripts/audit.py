#!/usr/bin/env python3
"""Audit a product's reportcard.yml and report what a new quarter needs.

Stdlib only -- no PyYAML, no node_modules. Parses the narrow YAML subset
this repo uses (mappings, sequences, scalars, wrapped plain scalars).

Usage:
    python3 audit.py _products/formsg/reportcard.yml [--quarter 2026-04-01]
"""

import argparse
import re
import sys
from pathlib import Path

KEY_RE = re.compile(r"^(\s*)(-\s+)?([A-Za-z_][\w\-]*):\s*(.*)$")
ITEM_RE = re.compile(r"^(\s*)-\s+(.*)$")


def unquote(v):
    v = v.strip()
    if v == "[]":
        return []
    if v == "{}":
        return {}
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v


def _significant(lines):
    """Drop blanks, comments, and wrapped plain-scalar continuation lines."""
    out = []
    for raw in lines:
        s = raw.rstrip()
        if not s.strip() or s.lstrip().startswith("#"):
            continue
        if KEY_RE.match(s) or ITEM_RE.match(s):
            out.append((len(s) - len(s.lstrip()), s.strip()))
    return out


def parse(lines):
    toks = _significant(lines)
    node, _ = _block(toks, 0, toks[0][0] if toks else 0)
    return node


def _block(toks, i, indent):
    """Parse every token at exactly `indent` into a dict or list."""
    if i >= len(toks):
        return {}, i

    if toks[i][1].startswith("- "):
        seq = []
        while i < len(toks) and toks[i][0] == indent and toks[i][1].startswith("- "):
            inner = toks[i][1][2:].strip()
            child_indent = indent + 2
            m = KEY_RE.match(inner)
            if m and not m.group(2):
                # "- key: value" -- a mapping starts on this line.
                entry = {}
                key, val = m.group(3), m.group(4).strip()
                i += 1
                if val:
                    entry[key] = unquote(val)
                else:
                    sub, i = _descend(toks, i, child_indent)
                    entry[key] = sub
                # remaining keys of the same mapping
                while i < len(toks) and toks[i][0] == child_indent:
                    m2 = KEY_RE.match(toks[i][1])
                    if not m2 or m2.group(2):
                        break
                    k2, v2 = m2.group(3), m2.group(4).strip()
                    i += 1
                    if v2:
                        entry[k2] = unquote(v2)
                    else:
                        sub, i = _descend(toks, i, child_indent + 2)
                        entry[k2] = sub
                seq.append(entry)
            else:
                seq.append(unquote(inner))
                i += 1
        return seq, i

    mapping = {}
    while i < len(toks) and toks[i][0] == indent:
        m = KEY_RE.match(toks[i][1])
        if not m or m.group(2):
            break
        key, val = m.group(3), m.group(4).strip()
        i += 1
        if val and val not in ("|", ">", ">-", "|-"):
            mapping[key] = unquote(val)
        else:
            sub, i = _descend(toks, i, indent + 2)
            mapping[key] = sub
    return mapping, i


def _descend(toks, i, expected):
    """Parse a nested block. Sequences may sit at the parent's indent."""
    if i >= len(toks):
        return {}, i
    actual = toks[i][0]
    if actual < expected and not toks[i][1].startswith("- "):
        return {}, i
    if actual < expected - 2:
        return {}, i
    return _block(toks, i, actual)


def resolve(node):
    return node


def dates(entries):
    out = []
    for e in entries or []:
        if isinstance(e, dict) and e.get("startDate"):
            out.append(str(e["startDate"]))
    return out


def qlabel(d):
    """'2026-01-01' -> 'Q1 2026'. Falls back to the raw date if off-cycle."""
    y, m, _ = (int(x) for x in d.split("-"))
    if m not in (1, 4, 7, 10):
        return d
    return f"Q{(m - 1) // 3 + 1} {y}"


def branch_name(product, target):
    """formsg + 2026-04-01 -> formsg-q2-2026-report-card"""
    y, m, _ = (int(x) for x in target.split("-"))
    return f"{product}-q{(m - 1) // 3 + 1}-{y}-report-card"


def branch_status(name):
    """Where does this branch already exist? Read-only; never mutates git."""
    import subprocess

    def git(*a, timeout=10):
        return subprocess.run(
            ["git", *a], capture_output=True, text=True, timeout=timeout
        )

    try:
        cur = git("rev-parse", "--abbrev-ref", "HEAD")
        if cur.returncode != 0:
            return "git unavailable (not a repo?)"
        current = cur.stdout.strip()

        local = git("rev-parse", "--verify", f"refs/heads/{name}").returncode == 0

        remote = None
        try:
            r = git("ls-remote", "--exit-code", "--heads", "origin", name, timeout=15)
            remote = r.returncode == 0
        except Exception:
            remote = None  # offline -- unknown, not absent

        if current == name:
            return "already on it"
        if local:
            return "exists locally -- switch to it"
        if remote:
            return "exists on REMOTE only -- someone may have started this quarter, ASK FIRST"
        if remote is None:
            return f"not found locally (remote unreachable); currently on '{current}'"
        return f"not found -- create it before the first write; currently on '{current}'"
    except Exception as e:
        return f"git check skipped ({type(e).__name__})"


def previous_quarter(d):
    y, m, _ = (int(x) for x in d.split("-"))
    m -= 3
    if m < 1:
        m += 12
        y -= 1
    return f"{y}-{m:02d}-01"


def next_quarter(d):
    y, m, _ = (int(x) for x in d.split("-"))
    m += 3
    if m > 12:
        m -= 12
        y += 1
    return f"{y}-{m:02d}-01"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--quarter", help="target quarter, e.g. 2026-04-01")
    ap.add_argument(
        "--active-only",
        action="store_true",
        help="only list metrics that carried a value last quarter; hide retired ones",
    )
    args = ap.parse_args()

    p = Path(args.path)
    if not p.exists():
        sys.exit(f"error: {p} not found")

    data = resolve(parse(p.read_text().splitlines()))

    # ---- work out the target quarter -------------------------------------
    all_dates = set()
    for e in (data.get("cost") or {}).get("values") or []:
        if isinstance(e, dict) and e.get("startDate"):
            all_dates.add(str(e["startDate"]))
    for g in data.get("metricGroups") or []:
        for mt in g.get("metrics") or []:
            all_dates.update(dates(mt.get("values")))

    if not all_dates:
        sys.exit("error: no dated entries found -- is this a reportcard.yml?")

    latest = max(all_dates)
    target = args.quarter or next_quarter(latest)

    print(f"product        : {data.get('projectId', '?')}")
    print(f"latest quarter : {latest} ({qlabel(latest)})")
    print(f"target quarter : {target} ({qlabel(target)})")
    print(f"table columns  : id | {qlabel(previous_quarter(target))} | {qlabel(target)}")
    bname = branch_name(data.get("projectId", "product"), target)
    print(f"branch         : {bname}")
    print(f"                 {branch_status(bname)}")
    if target in all_dates:
        print(f"\n!! {target} ALREADY EXISTS in this file -- check before appending.")
    print()

    # ---- team ------------------------------------------------------------
    members = (data.get("team") or {}).get("members") or []
    if members:
        last = members[-1]
        print(f"TEAM  last roster ({last.get('startDate')})")
        if target in dates(members):
            print(f"  already has {target}")
        for v in last.get("values") or []:
            inv = f", {v['involvement']}" if v.get("involvement") else ""
            print(f"  - {v.get('id')} ({v.get('role')}{inv})")
        print()

    # ---- cost ------------------------------------------------------------
    costs = (data.get("cost") or {}).get("values") or []
    if costs:
        last = costs[-1]
        print(f"COST  last entry ({last.get('startDate')})")
        for k in ("infra", "security", "manpower", "corporate", "tools", "others"):
            if k in last:
                print(f"  {k:<10} {last[k]}")
        if target in dates(costs):
            print(f"  -> {target} already present")
        else:
            print(
                f"  -> NO {target} cost entry. The quarter dropdown is built from\n"
                f"     cost.values alone, so {qlabel(target)} will NOT render until one\n"
                f"     exists -- metrics alone are not enough. Cost is blocking."
            )
        print()

    # ---- metrics ---------------------------------------------------------
    # A metric is "active" if it carried a value in the quarter immediately
    # before the target. Anything older was most likely retired on purpose.
    prev = previous_quarter(target)
    dormant = []

    print(f"METRICS  (active = has a {prev} value)")
    for g in data.get("metricGroups") or []:
        header_shown = False

        def header():
            nonlocal header_shown
            if not header_shown:
                print(f"\n  [{g.get('label')}]")
                header_shown = True

        for mt in g.get("metrics") or []:
            mid = mt.get("id")
            src = mt.get("source", "manual")
            if src != "manual":
                if not args.active_only:
                    header()
                    print(f"    auto {mid}: computed ({src}) -- nothing to enter")
                continue

            vals = mt.get("values") or []
            ds = dates(vals)
            if not ds:
                dormant.append((mid, "never", []))
                continue

            last_d, last_v = ds[-1], vals[-1].get("value")

            if target in ds:
                header()
                print(f"    OK   {mid}: {target} already present")
            elif last_d >= prev:
                header()
                print(f"    NEED {mid}: last {last_v} ({last_d})")
            else:
                gap = []
                d = next_quarter(last_d)
                while d < target:
                    gap.append(d)
                    d = next_quarter(d)
                dormant.append((mid, f"{last_v} ({last_d})", gap))

    if dormant and not args.active_only:
        print(f"\nDORMANT -- no {prev} value, likely retired. Skipped unless you say otherwise:")
        for mid, last, gap in dormant:
            missing = f", missing {len(gap)} quarter(s)" if gap else ""
            print(f"   {mid}: last {last}{missing}")
        print("   Ask once whether to revive or backfill any of these. Do not chase them.")
    elif dormant:
        print(f"\n({len(dormant)} dormant metric(s) hidden -- re-run without --active-only to see them)")

    # ---- changelog -------------------------------------------------------
    cl = p.parent / "CHANGELOG.md"
    if cl.exists():
        head = [l for l in cl.read_text().splitlines() if l.startswith("#")][:3]
        print(f"\nCHANGELOG.md  top headings: {head}")


if __name__ == "__main__":
    main()
