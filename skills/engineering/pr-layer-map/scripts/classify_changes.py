#!/usr/bin/env python3
"""Classify FormSG changed files into architectural layers.

Reads a diff (from a PR, a branch, or stdin) and emits JSON describing which
layers were touched, by how much, and which layer-to-layer edges are live.

The layer of a file is independent of whether it is a test. A spec sitting in
`app/models/__tests__/` still tells you the model layer moved, so test markers
are stripped from the path before classification and recorded on a separate
`kind` axis instead.

Pass --mermaid for a GitHub-ready diagram block instead of the JSON.

Usage:
    classify_changes.py --pr 9893 --mermaid [--repo opengovsg/FormSG]
    classify_changes.py --branch --mermaid      # base defaults to origin/HEAD
    git diff --numstat origin/develop... | classify_changes.py --stdin
"""

import argparse
import json
import re
import subprocess
import sys

# --- Layer definitions -------------------------------------------------------
# Each layer: id -> (label, group). `group` drives diagram placement.
LAYERS = {
    # Frontend
    "fe-shell":    ("App shell & routing", "frontend"),
    "fe-feature":  ("Features", "frontend"),
    "fe-ui":       ("UI kit & templates", "frontend"),
    "fe-state":    ("State & contexts", "frontend"),
    "fe-hooks":    ("Hooks", "frontend"),
    "fe-api":      ("API client", "frontend"),
    "fe-i18n":     ("i18n", "frontend"),
    "fe-utils":    ("Frontend utils & config", "frontend"),
    "fe-mocks":    ("MSW API mocks", "frontend"),
    "fe-other":    ("Frontend (other)", "frontend"),
    # Contract layer, imported by both sides
    "shared":      ("packages/shared", "contract"),
    "sdk":         ("packages/sdk", "contract"),
    # Backend
    "be-route":       ("Routes", "backend"),
    "be-middleware":  ("Middlewares", "backend"),
    "be-controller":  ("Controllers", "backend"),
    "be-service":     ("Services", "backend"),
    "be-model":       ("Models (Mongoose)", "backend"),
    "be-support":     ("Module support", "backend"),
    "be-types":       ("Backend types", "backend"),
    "be-utils":       ("Backend utils", "backend"),
    "be-infra":       ("Bootstrap & config", "backend"),
    "be-views":       ("Server-rendered views", "backend"),
    "be-other":       ("Backend (other)", "backend"),
    # Peripheral
    "email-templates": ("Email templates", "peripheral"),
    "services":        ("Lambdas & microservices", "peripheral"),
    "scripts":         ("Scripts & migrations", "peripheral"),
    "infra":           ("Infra & CI", "peripheral"),
    "docs":            ("Docs", "peripheral"),
    "e2e":             ("E2E tests", "peripheral"),
    "unknown":         ("Unclassified", "peripheral"),
}

# Ordered rules, first match wins. Applied to the test-stripped path.
# Order encodes the ambiguity resolutions: express loaders are bootstrap before
# they are middleware; a feature-level *Service.ts is api-client before it is a
# feature; a *.middleware.ts under routes/ or services/ is middleware first.
RULES = [
    # Non-application code
    (r"^__tests__/",                                        "e2e"),
    (r"^(docs/|\.claude/|[A-Z_]+\.md$|.*\.md$)",            "docs"),
    (r"^(deploy/|\.github/|\.husky/|\.localstack/)",        "infra"),
    (r"^(Dockerfile|docker-compose|init-|\.lintstagedrc|\.prettierrc|.*versionrc)", "infra"),
    (r"^scripts/",                                          "scripts"),
    (r"^(services/|functions/)",                            "services"),
    (r"^packages/react-email-preview/",                     "email-templates"),
    (r"^packages/sdk/",                                     "sdk"),
    (r"^packages/shared/",                                  "shared"),

    # Backend. Middleware wins over its host directory, except express loaders,
    # which are bootstrap wiring rather than a per-route concern.
    (r"^apps/backend/src/app/loaders/",                     "be-infra"),
    (r"^apps/backend/.*\.middlewares?\.ts$",                "be-middleware"),
    (r"^apps/backend/src/app/utils/(pipeline-middleware|limit-rate)\.ts$", "be-middleware"),
    (r"^apps/backend/src/app/routes/",                      "be-route"),
    (r"^apps/backend/.*\.routes\.ts$",                      "be-route"),
    (r"^apps/backend/.*\.controller\.ts$",                  "be-controller"),
    (r"^apps/backend/src/app/services/",                    "be-service"),
    (r"^apps/backend/.*\.service\.ts$",                     "be-service"),
    (r"^apps/backend/src/app/models/",                      "be-model"),
    (r"^apps/backend/.*\.(server\.)?(model|schema)\.ts$",   "be-model"),
    (r"^apps/backend/src/app/views/",                       "be-views"),
    (r"^apps/backend/src/app/utils/",                       "be-utils"),
    (r"^apps/backend/src/app/modules/",                     "be-support"),
    (r"^apps/backend/src/app/(config|constants)/",          "be-infra"),
    (r"^apps/backend/src/app/server\.ts$",                  "be-infra"),
    (r"^apps/backend/src/(types|shared)/",                  "be-types"),
    (r"^apps/backend/",                                     "be-other"),

    # Frontend. The api-client rules must precede features/, since feature-level
    # services live inside features/.
    (r"^apps/frontend/src/mocks/",                          "fe-mocks"),
    (r"^apps/frontend/src/services/",                       "fe-api"),
    (r"^apps/frontend/.*Service\.tsx?$",                    "fe-api"),
    (r"^apps/frontend/.*/(queries|mutations)\.ts$",         "fe-api"),
    (r"^apps/frontend/.*/mutations/",                       "fe-api"),
    (r"^apps/frontend/src/contexts/",                       "fe-state"),
    (r"^apps/frontend/.*(Store\.tsx?|store\.ts|Context\.tsx|Provider\.tsx)$", "fe-state"),
    (r"^apps/frontend/src/hooks/",                          "fe-hooks"),
    (r"^apps/frontend/.*/hooks/",                           "fe-hooks"),
    (r"^apps/frontend/src/(app|pages)/",                    "fe-shell"),
    (r"^apps/frontend/src/index\.tsx$",                     "fe-shell"),
    (r"^apps/frontend/src/i18n/",                           "fe-i18n"),
    (r"^apps/frontend/src/(components|templates|theme|assets)/", "fe-ui"),
    (r"^apps/frontend/src/features/",                       "fe-feature"),
    (r"^apps/frontend/src/(utils|constants|typings)/",      "fe-utils"),
    (r"^apps/frontend/",                                    "fe-other"),
]

# --- Diagram spine ----------------------------------------------------------
# The fine-grained layers above are the right resolution for classification but
# too fragmented for a PR description. These ten nodes are the stack a reviewer
# actually thinks in; each collapses one or more layers.
DIAGRAM = [
    ("feat",   "Pages &amp; features", "frontend",
     ["fe-shell", "fe-feature", "fe-state", "fe-hooks", "fe-i18n",
      "fe-utils", "fe-mocks", "fe-other"]),
    ("feui",   "UI components",  "frontend", ["fe-ui"]),
    ("feapi",  "API client",     "frontend", ["fe-api"]),
    ("shared", "packages/shared", "contract", ["shared"]),
    ("sdk",    "packages/sdk",    "contract", ["sdk"]),
    ("route",  "Routes",          "backend",  ["be-route"]),
    ("mw",     "Middlewares",     "backend",  ["be-middleware"]),
    ("ctrl",   "Controllers",     "backend",  ["be-controller"]),
    ("svc",    "Services",        "backend",  ["be-service", "be-support"]),
    ("val",    "Validation &amp; utils", "backend", ["be-utils"]),
    ("model",  "Models",          "backend",  ["be-model", "be-types"]),
]

# Solid edges are the request path; dotted edges are compile-time imports.
DIAGRAM_EDGES = [
    ("feat", "feui", "solid"),
    ("feat", "feapi", "solid"),
    ("feapi", "route", "http"),
    ("route", "mw", "solid"),
    ("mw", "ctrl", "solid"),
    ("ctrl", "svc", "solid"),
    ("svc", "val", "solid"),
    ("svc", "model", "solid"),
    # One import edge per side. Both frontend and backend import the contract
    # packages from many places; drawing every one buries the request path under
    # crossing lines without telling a reviewer anything more.
    ("feat", "shared", "dotted"),
    ("model", "shared", "dotted"),
    ("feat", "sdk", "dotted"),
    ("svc", "sdk", "dotted"),
]

# Layers outside the spine. Touched ones become a footnote rather than a node,
# so the request path stays readable.
PERIPHERAL = ["be-infra", "be-views", "email-templates", "services",
              "scripts", "infra", "docs", "e2e", "unknown"]

TEST_SEGMENT = re.compile(r"(^|/)(__tests__|__mocks__|spec)/")
TEST_SUFFIX = re.compile(r"\.(spec|test)\.(ts|tsx|js|jsx)$")
STORY_SUFFIX = re.compile(r"\.stories\.(tsx?|jsx?)$")


def kind_of(path):
    """Classify a path on the test axis, independent of its layer."""
    if STORY_SUFFIX.search(path):
        return "story"
    if TEST_SUFFIX.search(path) or TEST_SEGMENT.search(path):
        return "test"
    if re.search(r"(^|/)(jest\.config|vitest\.config|vitest-setup|playwright\.config|test-utils)", path):
        return "test"
    if path.startswith("apps/frontend/src/mocks/"):
        return "test"
    return "source"


def strip_test_markers(path):
    """Remove test scaffolding from a path so it classifies to its real layer."""
    path = re.sub(r"(^|/)(__tests__|__mocks__)/", r"\1", path)
    path = TEST_SUFFIX.sub(r".\2", path)
    path = STORY_SUFFIX.sub(r".\1", path)
    return path


def layer_of(path):
    stripped = strip_test_markers(path)
    for pattern, layer in RULES:
        if re.search(pattern, stripped):
            return layer
    return "unknown"


def parse_numstat(text):
    """Parse `git diff --numstat` into (path, added, deleted) triples."""
    out = []
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        add, delete, path = parts[0], parts[1], parts[2]
        # Renames arrive as `old => new`; keep the destination.
        if " => " in path:
            path = re.sub(r"\{(.*) => (.*)\}", r"\2", path)
            if " => " in path:
                path = path.split(" => ")[-1]
        added = 0 if add == "-" else int(add)
        deleted = 0 if delete == "-" else int(delete)
        out.append((path.strip(), added, deleted))
    return out


def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        if not check:
            return None
        sys.exit(f"command failed: {' '.join(cmd)}\n{r.stderr.strip()}")
    return r.stdout


def resolve_base(base):
    """Find a usable base ref.

    FormSG's default branch is `develop`, and a fresh clone often has no local
    ref for it at all — only `origin/develop`. Passing the bare name straight to
    merge-base fails with a bare "Not a valid object name", so try the local
    name, then the remote-tracking one, then the remote's own HEAD.
    """
    if base:
        for candidate in (base, f"origin/{base}"):
            if run(["git", "rev-parse", "--verify", "-q", candidate], check=False):
                return candidate
        sys.exit(f"base ref not found: tried {base} and origin/{base}")

    head = run(["git", "symbolic-ref", "refs/remotes/origin/HEAD"], check=False)
    if head:
        return head.strip().replace("refs/remotes/", "")
    for candidate in ("origin/develop", "origin/main", "develop", "main"):
        if run(["git", "rev-parse", "--verify", "-q", candidate], check=False):
            return candidate
    sys.exit("could not determine a base branch; pass --base explicitly")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr", help="PR number or URL")
    ap.add_argument("--repo", default="opengovsg/FormSG")
    ap.add_argument("--branch", action="store_true", help="diff current branch against its merge-base")
    ap.add_argument("--base", default=None,
                    help="base branch; defaults to the remote HEAD (develop on FormSG)")
    ap.add_argument("--stdin", action="store_true", help="read git numstat from stdin")
    ap.add_argument("--mermaid", action="store_true",
                    help="emit a GitHub-ready mermaid block instead of JSON")
    ap.add_argument("--no-counts", action="store_true",
                    help="with --mermaid, omit the +/- line counts from nodes")
    args = ap.parse_args()

    meta = {}
    if args.pr:
        pr = str(args.pr).rstrip("/").split("/")[-1]
        # The API returns per-file counts already combined across commits.
        # `gh pr diff` concatenates per-commit patches instead, which counts a
        # file once per commit that touched it and inflates the totals.
        rows = run([
            "gh", "api", "--paginate",
            f"repos/{args.repo}/pulls/{pr}/files",
            "--jq", '.[] | [.additions, .deletions, .filename, .status] | @tsv',
        ])
        files, statuses = [], {}
        for line in rows.splitlines():
            if not line.strip():
                continue
            add, delete, path, status = (line.split("\t") + ["modified"])[:4]
            files.append((path, int(add), int(delete)))
            statuses[path] = status
        info = json.loads(run([
            "gh", "pr", "view", pr, "--repo", args.repo,
            "--json", "number,title,author,state,headRefName,baseRefName,url",
        ]))
        meta = {
            "source": f"PR #{info['number']}",
            "title": info["title"],
            "author": info.get("author", {}).get("login"),
            "state": info["state"],
            "branch": info.get("headRefName"),
            "base": info.get("baseRefName"),
            "url": info["url"],
        }
    elif args.stdin:
        files = parse_numstat(sys.stdin.read())
        statuses = {}
        meta = {"source": "stdin"}
    else:
        base_ref = resolve_base(args.base)
        base = run(["git", "merge-base", "HEAD", base_ref]).strip()
        branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()
        files = parse_numstat(run(["git", "diff", "--numstat", base, "HEAD"]))
        statuses = {}
        for line in run(["git", "diff", "--name-status", base, "HEAD"]).splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                code = parts[0][0]
                statuses[parts[-1]] = {
                    "A": "added", "D": "removed", "R": "renamed",
                }.get(code, "modified")
        meta = {"source": f"branch {branch}", "branch": branch, "base": base_ref}

    # Aggregate
    layers = {}
    for path, added, deleted in files:
        lid = layer_of(path)
        k = kind_of(path)
        L = layers.setdefault(lid, {
            "id": lid,
            "label": LAYERS.get(lid, (lid, "peripheral"))[0],
            "group": LAYERS.get(lid, (lid, "peripheral"))[1],
            "files": [], "added": 0, "deleted": 0,
            "counts": {"source": 0, "test": 0, "story": 0},
        })
        L["files"].append({
            "path": path, "added": added, "deleted": deleted, "kind": k,
            "status": statuses.get(path, "modified"),
        })
        L["added"] += added
        L["deleted"] += deleted
        L["counts"][k] += 1

    for L in layers.values():
        L["files"].sort(key=lambda f: (-(f["added"] + f["deleted"]), f["path"]))
        # A layer whose only changes are tests/stories did not move structurally.
        L["source_touched"] = L["counts"]["source"] > 0
        L["new_files"] = sum(1 for f in L["files"] if f["status"] == "added")

    touched = set(layers)
    node_touched = {
        nid: any(l in touched for l in layer_ids)
        for nid, _, _, layer_ids in DIAGRAM
    }
    edges = [
        {"from": a, "to": b, "style": style,
         "live": node_touched[a] and node_touched[b]}
        for a, b, style in DIAGRAM_EDGES
    ]

    result = {
        "meta": meta,
        "totals": {
            "files": len(files),
            "added": sum(f[1] for f in files),
            "deleted": sum(f[2] for f in files),
            "layers_touched": len(layers),
            "layers_source_touched": sum(1 for L in layers.values() if L["source_touched"]),
        },
        "layers": sorted(layers.values(), key=lambda L: -(L["added"] + L["deleted"])),
        "all_layers": [
            {"id": k, "label": v[0], "group": v[1], "touched": k in touched}
            for k, v in LAYERS.items()
        ],
        "edges": edges,
    }

    if args.mermaid:
        sys.stdout.write(render_mermaid(result, show_counts=not args.no_counts) + "\n")
    else:
        json.dump(result, sys.stdout, indent=2)
        sys.stdout.write("\n")


def render_mermaid(result, show_counts=True):
    """Emit a Mermaid block that renders correctly in a GitHub PR description.

    GitHub renders the diagram against either its light or its dark theme and
    gives no way to detect which, so nothing here may depend on the page
    background. Touched nodes get a solid fill with explicit white text;
    untouched nodes use `fill:none` so they take whatever background they land
    on. That keeps one diagram legible in both themes.
    """
    by_layer = {L["id"]: L for L in result["layers"]}

    nodes = []
    for nid, label, group, layer_ids in DIAGRAM:
        hit = [by_layer[l] for l in layer_ids if l in by_layer]
        added = sum(L["added"] for L in hit)
        deleted = sum(L["deleted"] for L in hit)
        source = any(L["source_touched"] for L in hit)
        nodes.append({
            "id": nid, "label": label, "group": group,
            "touched": bool(hit), "source": source,
            "added": added, "deleted": deleted,
        })
    node_by_id = {n["id"]: n for n in nodes}

    groups = [
        ("FE", "Frontend", "frontend"),
        ("CT", "Shared contracts", "contract"),
        ("BE", "Backend", "backend"),
    ]
    group_label = {g: label for _, label, g in groups}

    def style_block(members):
        lines = [
            "  classDef touched fill:#1f6feb,stroke:#1f6feb,stroke-width:1px,color:#ffffff;",
            "  classDef tests fill:none,stroke:#1f6feb,stroke-width:2px,color:#1f6feb;",
            "  classDef dim fill:none,stroke:#8b949e,stroke-width:1px,color:#8b949e,stroke-dasharray:4 3;",
        ]
        for cls, pick in [
            ("touched", lambda n: n["touched"] and n["source"]),
            ("tests",   lambda n: n["touched"] and not n["source"]),
            ("dim",     lambda n: not n["touched"]),
        ]:
            ids = [n["id"] for n in members if pick(n)]
            if ids:
                lines.append(f"  class {','.join(ids)} {cls};")
        return lines

    def label_for(n):
        text = n["label"]
        if show_counts and n["touched"] and (n["added"] or n["deleted"]):
            text += f"<br/><b>+{n['added']} −{n['deleted']}</b>"
        return text

    def footnote():
        extra = [by_layer[p] for p in PERIPHERAL if p in by_layer]
        if not extra:
            return []
        names = ", ".join(f"{L['label']} (+{L['added']} −{L['deleted']})" for L in extra)
        return ["", f"_Also touched: {names}._"]

    # A contained change does not need the whole stack drawn around it. When the
    # touched nodes sit inside one group and there are only a couple, render that
    # group's chain on a single row and state in words that the rest is
    # untouched — the full diagram spends most of its height on dim boxes making
    # exactly that point.
    #
    # Contract-only changes are excluded on purpose: packages/shared and
    # packages/sdk are imported from everywhere, so the wide view is the whole
    # story, and the two nodes have no edge between them to form a chain from.
    touched_nodes = [n for n in nodes if n["touched"]]
    touched_groups = {n["group"] for n in touched_nodes}
    if (len(touched_groups) == 1 and len(touched_nodes) <= 3
            and touched_groups <= {"frontend", "backend"}):
        gkey = next(iter(touched_groups))
        members = [n for n in nodes if n["group"] == gkey]
        member_ids = {n["id"] for n in members}

        out = ["```mermaid", "flowchart LR"]
        out += [f'  {n["id"]}["{label_for(n)}"]' for n in members]
        live = []
        for a, b, style in DIAGRAM_EDGES:
            if a in member_ids and b in member_ids:
                arrow = {"solid": "-->", "dotted": "-.->", "http": "==>"}[style]
                out.append(f"  {a} {arrow} {b}")
                live.append(node_by_id[a]["touched"] and node_by_id[b]["touched"])
        out += style_block(members)
        out += [f"  linkStyle {i} stroke:#8b949e,stroke-width:1px,opacity:0.35;"
                for i, ok in enumerate(live) if not ok]
        out.append("```")

        rest = [group_label[g].lower() for _, _, g in groups if g != gkey]
        out += ["", f"_Contained to the {group_label[gkey].lower()} — "
                    f"{' and '.join(rest)} untouched._"]
        return "\n".join(out + footnote())

    # Top-to-bottom so the groups stack the way the architecture does, with
    # each group's nodes side by side. A left-to-right flow produces a very wide
    # strip that a PR description column will squash.
    out = ["```mermaid", "flowchart TB"]
    for gid, glabel, gkey in groups:
        out.append(f'  subgraph {gid}["{glabel}"]')
        out.append("    direction LR")
        out += [f'    {n["id"]}["{label_for(n)}"]'
                for n in nodes if n["group"] == gkey]
        out.append("  end")

    for a, b, style in DIAGRAM_EDGES:
        # The thick arrow marks the network boundary. It carries no text label:
        # mermaid draws edge labels on an opaque light pill, which reads as a
        # rendering glitch against GitHub's dark canvas.
        arrow = {"solid": "-->", "dotted": "-.->", "http": "==>"}[style]
        out.append(f"  {a} {arrow} {b}")

    # Styling. Explicit colors on both fill and text, chosen to hold up against
    # GitHub's light and dark canvases alike.
    out += style_block(nodes)
    # Mermaid's default subgraph fill is an opaque pastel that only suits a light
    # canvas. Clearing it lets the group boxes sit on either GitHub theme.
    for gid, _, _ in groups:
        out.append(f"  style {gid} fill:none,stroke:#8b949e,stroke-width:1px,color:#8b949e;")

    # Fade edges that do not connect two touched nodes, so the live path reads
    # at a glance instead of competing with the untouched scaffolding.
    for i, (a, b, _) in enumerate(DIAGRAM_EDGES):
        if not (node_by_id[a]["touched"] and node_by_id[b]["touched"]):
            out.append(f"  linkStyle {i} stroke:#8b949e,stroke-width:1px,opacity:0.35;")

    out.append("```")
    return "\n".join(out + footnote())


if __name__ == "__main__":
    main()
