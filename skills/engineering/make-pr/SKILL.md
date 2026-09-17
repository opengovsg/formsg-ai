---
name: make-pr
description: Assemble a human-readable, review-ready PR body and inline comments from the diff, commit messages, and the implementation conversation. Use when the user has finished implementation on a branch and wants to ship for review.
---

# Make PR

Author-side companion to `review`. Moves rationale from where it lives (the diff, the commits, the conversation that produced them) into where reviewers look (PR body, inline comments). Does not invent rationale — if the *why* of a change is unrecoverable, ask the user.

## Workflow

1. **Pin the fixed point** — use user-supplied ref, else `main`. Capture `git diff <fixed-point>...HEAD` and `git log <fixed-point>..HEAD --oneline`.

2. **Collect rationale** — primary sources, in order:
   - The diff itself and the commit messages.
   - The current conversation, if this session did the implementation.
   - Optional extras when present: `.scratch/<feature>/decisions.md` breadcrumbs, ADRs in `docs/adr/` touching diff paths, a linked issue/PRD. Never require these; never emit placeholders for their absence.

3. **Assemble PR body** — follow [TEMPLATE.md](TEMPLATE.md). Omit any section whose source is empty.

4. **Screenshots (frontend only)** — if the diff touches frontend files, follow [SCREENSHOTS.md](SCREENSHOTS.md).

5. **Build inline comments** — one comment per decision point a reviewer would otherwise question: a rejected alternative, a non-obvious constraint, a "this looks wrong but isn't" spot. Source from `kind: inline` breadcrumbs when they exist, else from the conversation and diff. Each is `{ file, line, body }`, ≤3 sentences, and answers "why this way" — never "what this does". Max ~5 per PR; if nothing qualifies, post none.

6. **Preview** — show assembled body, inline comment list, and push plan. Wait for explicit approval.

7. **Open PR** — after approval:
   - `git push -u origin <branch>` if no upstream, else `git push`
   - `gh pr create --title "<title>" --body-file <tmp>`
   - Post each inline comment via `gh api repos/{owner}/{repo}/pulls/{n}/comments`
   - Print PR URL
