---
name: review
description: Review the changes since a fixed point (commit, branch, tag, or merge-base) along four independent axes — Standards, Spec, Architecture, and Divergent design — each run as a parallel sub-agent so contexts stay clean, then verified against false positives and reported side by side. Use when the user wants to review a branch, a PR, work-in-progress changes, or asks to "review since X".
---

# Review

Multi-axis review of the diff between `HEAD` and a fixed point — the PR's target branch by default (see step 1). Each axis runs as its own **parallel sub-agent** so they don't pollute each other's context. Findings are then verified against false positives and aggregated **without merging the axes** — the user evaluates each independently.

The four axes:

- **Standards** — does the code follow the repo's documented standards? And are those standards themselves sound, or tech debt worth flagging?
- **Spec** — does the code faithfully implement the originating issue / PRD / spec?
- **Architecture** — are there deepening opportunities in the changed code? (lens of `/improve-codebase-architecture`)
- **Divergent** — for each change, was this the best option among the alternatives, given the PR's scope?

## Process

### 1. Pin the fixed point

The fixed point is the **PR's target branch** — the branch this work merges into. Don't ask; resolve it:

- If the branch has a PR, read its base: `gh pr view --json baseRefName -q .baseRefName`.
- No PR? Fall back to the repo's default branch: `gh repo view --json defaultBranchRef -q .defaultBranchRef.name` (usually `main`).
- Only use something else if the user **explicitly** named a different fixed point (a commit SHA, tag, `HEAD~5`, etc.) — then pass theirs through verbatim.

Capture the diff command once: `git diff <fixed-point>...HEAD` (three-dot, against the merge-base) — this is what gets reviewed. Note the commit list via `git log <fixed-point>..HEAD --oneline`; it's context for understanding the change and finding the spec, **not** a review target. The review is scoped to the code in the diff, not commit messages, PR titles/descriptions, or branch names.

### 2. Identify the spec source

Look for the originating spec, in this order:

1. Issue references in commit messages (`#123`, `Closes #45`, GitLab `!67`) - fetch via project's issue tracker.
2. A path the user passed as an argument.
3. A PRD/spec file under `docs/`, `specs/`, or `.scratch/` matching the branch or feature.
4. If nothing is found, ask. If there's no spec, the **Spec** axis skips and reports "no spec available".

### 3. Identify the standards sources

Anything documenting how code should be written: `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, `CONTEXT.md` / `CONTEXT-MAP.md`, `docs/adr/`, `STYLE.md` / `STANDARDS.md`, and config files (`eslint.config.*`, `biome.json`, `tsconfig.json` — note them but don't re-check what tooling enforces). Collect the file list; the **Standards** sub-agent reads them. Skip docs that govern commit messages or PR conventions rather than code (e.g. `commit-style.md`) — the review is scoped to code.

### 4. Triage, then spawn the axis sub-agents in parallel

**Triage first (one judgment call, no formulas):** is there anything substantive to reason about?

- Unambiguously cosmetic — docs/comments/formatting only, a version bump, a generated-file change → run **Standards + Spec** only; skip Architecture and Divergent. Note that you did.
- Clearly automated or no-op (e.g. a dependabot bump that CI already gates) → skip the review with a one-line "nothing substantive to review."
- Anything else, or any doubt → run **all four**. Bias toward running more: a one-line change can be load-bearing (a tweak to a security check is exactly the `isV4` case). Collapse only when it's obviously just cosmetic.

Then send a single message with one `Agent` call per applicable axis (`general-purpose` subagent for all). **Don't read the diff or docs yourself** — stay a thin dispatcher. Tell each sub-agent to read its own brief file and follow it, passing only the diff command, the commit list (context only — not a review target), and the source paths it needs:

- **Standards** → `axes/standards.md` (+ the standards-source paths from step 3)
- **Spec** → `axes/spec.md` (+ the spec path) — skip if no spec exists; note it in the report
- **Architecture** → `axes/architecture.md`
- **Divergent** → `axes/divergent.md`

Every brief follows the shared finding contract (`axes/_contract.md`) — a ~400-word cap and a confidence score + evidence per finding — so the filter in step 5 has what it needs.

### 5. Verify each finding against false positives

Collect the findings the axis agents returned and run them all through the gate in [FILTER.md](FILTER.md) before aggregating: independent per-finding verification, dedup by file+line, and a per-axis disposition that drops the rest. This gate is what makes autonomous posting safe — a finding the author dismisses costs more credibility than a missed nit. [FILTER.md](FILTER.md) is the single source of truth for the mechanics, rubric, thresholds, and the always-drop list; follow it rather than re-deriving them here.

### 6. Aggregate

Present each surviving finding under its axis heading (`## Standards`, `## Spec`, `## Architecture`, `## Divergent`), lightly cleaned. Do **not** merge or rerank *across* axes — the separation is the point (the file+line dedup in step 5 is the only cross-axis merge). End with a one-line summary: surviving findings per axis, the single worst issue, and how many were dropped below threshold (no silent truncation).

### 7. (Optional) Post as PR comments

Only if the user asked to post. **Post one batched review** (`gh api .../pulls/{n}/reviews` with a `comments[]` array) — every surviving finding anchored **inline on its line(s)**, never an unanchored `gh pr comment`. Standards/Spec comments carry their numeric `confidence`; Architecture/Divergent don't. Cross-cutting findings with no single line go in the review's summary body. **If nothing survived, say so — don't manufacture nits.** **If the PR was already reviewed by this tool, re-evaluate against the prior comments, the author's replies, and commits pushed since — post only the delta, never a repost.** Skip closed/merged/draft PRs. Format, labels, AI disclaimer, empty-review path, and re-review logic: [COMMENTS.md](COMMENTS.md).

## Why separate axes

A change can pass one axis and fail another:

- Follows every standard but implements the wrong thing → **Standards pass, Spec fail.**
- Does exactly what the issue asked but breaks conventions → **Spec pass, Standards fail.**
- Correct and conventional, but a shallow module or a worse-than-the-alternative choice → caught only by **Architecture** / **Divergent.**

Reporting them separately stops one axis from masking another.
