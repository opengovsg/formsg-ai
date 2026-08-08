---
name: split-prs
description: Reorganize a large PR or branch into a gh-stack of deployable slices — each safe to merge and ship alone, review-by-commit, prepared with the review template.
disable-model-invocation: true
---

# Split PRs

Turn one pile of work into a **gh-stack** of **deployable slices**. Rewrite freely (reorder, fixup, squash) so each slice is **review-by-commit** and safe to ship alone. Keep the **grain** coarse — split only when review clarity or deploy risk earns it.

Requires `docs/agents/commit-style.md` and the `gh` stack extension (`gh extension install github/gh-stack`). Run `/setup-formsg-ai-skills` if commit style is missing. Deployability and grain rules: [DEPLOYABLE.md](DEPLOYABLE.md). PR titles and bodies inherit the review voice from [TEMPLATE.md](../prepare-for-review/TEMPLATE.md).

**Gate:** propose the plan and wait for approval before rewriting history, creating branches, pushing, or opening PRs. Snapshot first (`git stash create` → `refs/backup/pre-split-<timestamp>`).

## Process

### 1. Survey

Pin trunk (PR base if one exists, else repo default). Capture `git diff <trunk>...HEAD`, `git log <trunk>..HEAD --oneline`, the existing PR body if any, and intent from chat / breadcrumbs / issue refs. Note ownership signals (`CODEOWNERS`) when they suggest natural cuts.

**Done when:** trunk, diff, commit list, and intent sources are in hand.

### 2. Propose the stack

Draft the coarsest set of deployable slices that still improve review or risk. For each slice, list:

- **Title** — one-line why; subject shape from `docs/agents/commit-style.md`, voice from [TEMPLATE.md](../prepare-for-review/TEMPLATE.md) (matter-of-fact, ASD-STE100, `CONTEXT.md` language, meaning not labels)
- **Scope** — paths / concerns included
- **Deployable because…** — dormant, flag-gated, additive, pure refactor, expand/contract step, etc. (per [DEPLOYABLE.md](DEPLOYABLE.md))
- **Commits (planned)** — the review-by-commit narrative inside the slice

Show a Mermaid diagram: trunk → bottom → … → top. Justify the grain: why adjacent slices stay apart, or why one slice is enough.

Ask: "Approve this stack, or adjust the grain?"

**Done when:** user approves the slice list and order.

### 3. Rebuild history into the stack

Only after approval. Ensure `gh stack` is available; trunk = `--base` when not the repo default.

1. Snapshot the pre-split tip (backup ref above).
2. Rebuild bottom-up with non-interactive `gh stack` only — named branches on `init`/`add`/`checkout`, `submit --auto`, `view --json`. Stage named paths/hunks; write **review-by-commit** history per `docs/agents/commit-style.md` (fixup, reorder, squash as needed so each commit is one logical step). Prefer a single-commit slice when the story fits one subject — `submit --auto` then titles the PR from that subject.
3. Mid-stack fix → navigate down, commit there, `gh stack rebase --upstack`, then continue. Put each change on the branch that owns that concern.

```bash
gh stack init --base <trunk> <bottom-branch>
# stage → commit (repeat for review-by-commit narrative)
gh stack add <next-branch>
# …
gh stack submit --auto
gh stack view --json
```

**Done when:** `gh stack view --json` shows the approved layers with PRs, bottom → top.

### 4. Prepare each PR for review

For every slice, follow `prepare-for-review`. Read [TEMPLATE.md](../prepare-for-review/TEMPLATE.md) in full before writing — its opening voice (matter-of-fact, ASD-STE100, ubiquitous language from `CONTEXT.md`; sources feed you, bodies carry meaning not labels) and the section template both apply. Titles use the same voice plus the subject shape in `docs/agents/commit-style.md`. Assemble the body (omit empty sub-sections), collect inline comments from breadcrumbs, preview, then apply with `gh pr edit` / review comments (PRs already exist from `submit` — use edit, not create).