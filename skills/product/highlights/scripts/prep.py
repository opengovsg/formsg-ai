#!/usr/bin/env python3
"""Prepare a highlights scan: quarter bounds + last changelog entry as the format template.

Stdlib only.

Usage:
    python3 prep.py formsg                # infers the quarter after the latest logged
    python3 prep.py formsg --quarter q2-2026
"""

import argparse
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^##\s+Q([1-4])\s+(\d{4})\b(.*)$")
MONTHS = {1: ("Jan-Mar", "01", "03-31"), 2: ("Apr-Jun", "04", "06-30"),
          3: ("Jul-Sep", "07", "09-30"), 4: ("Oct-Dec", "10", "12-31")}


def parse_quarter(s):
    m = re.fullmatch(r"[qQ]?([1-4])[-_ /]?(\d{4})", s.strip()) or \
        re.fullmatch(r"(\d{4})[-_ /]?[qQ]?([1-4])", s.strip())
    if not m:
        sys.exit(f"error: could not read quarter '{s}'. Try q2-2026.")
    a, b = m.group(1), m.group(2)
    return (int(a), int(b)) if len(b) == 4 else (int(b), int(a))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("product")
    ap.add_argument("--quarter", help="e.g. q2-2026")
    ap.add_argument("--root", default=".", help="repo root")
    args = ap.parse_args()

    cl = Path(args.root) / "_products" / args.product / "CHANGELOG.md"
    if not cl.exists():
        sys.exit(f"error: {cl} not found -- check the product id")

    lines = cl.read_text().splitlines()
    entries = [(i, m) for i, l in enumerate(lines) if (m := HEADING.match(l))]
    if not entries:
        sys.exit(f"error: no '## Q<n> <year>' headings in {cl}")

    last_i, last_m = entries[0]
    last_q, last_y = int(last_m.group(1)), int(last_m.group(2))

    if args.quarter:
        q, y = parse_quarter(args.quarter)
    else:
        q, y = (last_q + 1, last_y) if last_q < 4 else (1, last_y + 1)

    label, start_mm, end_md = MONTHS[q]
    print(f"product        : {args.product}")
    print(f"target quarter : Q{q} {y} ({label})")
    print(f"date range     : {y}-{start_mm}-01 to {y}-{end_md}")
    print(f"heading to add : ## Q{q} {y} {label}")
    print(f"latest logged  : Q{last_q} {last_y}")

    if (y, q) == (last_y, last_q):
        print(f"\n!! Q{q} {y} IS ALREADY IN THE CHANGELOG -- check before adding another.")
    gap = (y - last_y) * 4 + (q - last_q)
    if gap > 1:
        print(f"\n!! GAP: {gap - 1} quarter(s) missing between Q{last_q} {last_y} and target.")

    # ---- last entry, verbatim: this IS the format to mirror -----------------
    end = entries[1][0] if len(entries) > 1 else len(lines)
    block = lines[last_i:end]

    # Only count labels that sit inside a "- Metrics" block, i.e. indented
    # deeper than the Metrics bullet itself.
    labels, metrics_indent = set(), None
    for l in block:
        if not l.strip():
            continue
        indent = len(l) - len(l.lstrip())
        if re.match(r"^\s*-\s+Metrics\s*:?\s*$", l):
            metrics_indent = indent
            continue
        if metrics_indent is None:
            continue
        if indent <= metrics_indent:
            metrics_indent = None
            continue
        if m := re.match(r"^\s*-\s+([A-Za-z][A-Za-z ()]*?)\s*:", l):
            labels.add(m.group(1).strip())
    labels = sorted(labels)
    groups = [l.strip()[2:] for l in block if re.match(r"^-\s+\S", l)]

    print(f"\ntop-level groups used last quarter: {groups}")
    print(f"metric labels used last quarter    : {labels}")
    print("\nIf a feature carried a metric last quarter, it needs one this quarter --")
    print("a real value or an explicit [Placeholder]. Never a guess.")
    print("\n" + "=" * 70)
    print("LAST ENTRY VERBATIM -- mirror this structure exactly")
    print("=" * 70)
    print("\n".join(block).rstrip())


if __name__ == "__main__":
    main()
