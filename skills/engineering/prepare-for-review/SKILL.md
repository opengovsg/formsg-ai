---
name: prepare-for-review
description: Assemble a review-ready PR body and inline comments from the breadcrumbs the implementation loop captured, the ADRs in the touched area, and the originating PRD. Use when the user has finished implementation on a branch and wants to ship for review.
---

# Prepare for Review

Author-side companion to `review`. Moves rationale from where it was captured (breadcrumbs, ADRs, PRD) into where reviewers look (PR body, inline comments). Does not generate rationale — empty sources produce omitted sections.

Requires `docs/agents/issue-tracker.md` and `docs/agents/decisions-breadcrumb.md`. Run `/setup-matt-pocock-skills` if missing.

## Workflow

1. **Pin the fixed point** — use user-supplied ref, else `main`. Capture `git diff <fixed-point>...HEAD` and `git log <fixed-point>..HEAD --oneline`.

2. **Collect rationale sources**
   - Breadcrumbs: `.scratch/<feature>/decisions.md` (optional)
   - ADRs: `docs/adr/` files touching paths in the diff
   - PRD/issue: from commit message refs via `docs/agents/issue-tracker.md`, else `.scratch/<feature>/prd.md`. Ask user if absent.

3. **Assemble PR body** — follow [TEMPLATE.md](TEMPLATE.md). Omit any sub-section whose source is empty.

4. **Screenshots (frontend only)** — if diff touches frontend files, follow [SCREENSHOTS.md](SCREENSHOTS.md).

5. **Build inline comments** — one comment per `kind: inline` breadcrumb: `{ file, line, body }`. Surface malformed entries (missing `file`/`line`) to user.

6. **Preview** — show assembled body, inline comment list, and push plan. Wait for explicit approval.

7. **Open PR** — after approval:
   - `git push -u origin <branch>` if no upstream, else `git push`
   - `gh pr create --title "<title>" --body-file <tmp>`
   - Post each inline comment via `gh api repos/{owner}/{repo}/pulls/{n}/comments`
   - Print PR URL
