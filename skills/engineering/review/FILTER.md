# False-positive filter

Adapted from Anthropic's `/code-review`. Findings the user dismisses cost more credibility than findings you miss. Every finding from every axis passes through this before aggregation.

## How to run it

**Correctness axes (Standards/Spec): one verifier per finding, in parallel.** Each verifier gets only the diff, the one finding, and the standards-file list — **not** the originating axis's reasoning (the finder is the worst judge of its own finding). Verify on **Haiku** (`Agent(..., model: "haiku")`; in a Workflow, `agent(prompt, {model: "haiku"})`). Locating a bug against the rubric is cheap, and stays cheap only because it's Haiku + single-finding + parallel — don't hand one agent all findings.

**Judgement axes (Architecture/Divergent): no verifier sub-agent.** Their gate lives in the axis brief itself — a finding only survives the finder when the reasoning holds and the alternative is genuinely better for the PR's scope. The orchestrator takes these findings as-is, applying only the always-drop list below and the dedup step. Surface the strongest few.

The correctness verifier:

1. **Locates the finding** via its cited `file:line` + quoted code — best-effort: an off-by-a-few line or a cross-cutting finding still counts as located if its quoted code is in the diff. Score **0** only when the finding can't be tied to the changed code at all (the quote matches nothing) — that's the unfalsifiable, likely-hallucinated case the gate exists to catch.
2. For a finding against a documented standard, **confirms the doc actually says it** — "CLAUDE.md says so" doesn't count if the rule isn't there.
3. Scores it **0–100** against the rubric below, and returns its verdict + one line of evidence.

### Dedup

The same file+line gets flagged by two axes (commonly Architecture **and** Divergent) and survives twice. The orchestrator merges them — keep the higher score where they carry one, cite both axes. A text-merge, not another agent.

### Rubric (correctness axes — give to the scoring agent verbatim)

- **0** — False positive that doesn't survive light scrutiny, or a pre-existing issue.
- **25** — Might be real, couldn't verify; if stylistic, not named in a standards doc.
- **50** — Verified real, but a nitpick or rare in practice.
- **75** — Double-checked; likely hit in practice, or directly named in a standards doc.
- **100** — Evidence confirms a real issue that will happen frequently.

### Disposition — a 70 doesn't mean the same thing on every axis

The rubric is calibrated for *bug-likelihood*, so a single cutoff would filter out the design feedback this skill exists to surface:

- **Standards & Spec (correctness):** the finding claims something is *wrong* → **drop everything below 70**.
- **Architecture & Divergent (judgement):** no numeric cutoff and no verifier — the *reasoning holds and the alternative is genuinely better* gate is already enforced by the finder (see its brief), so there's nothing to re-score here. Just dedup and apply the always-drop list. Surface the strongest few.

If an axis has no surviving finding, report it clean.

## Always false positives — drop without scoring

- Non-committed code. 
- Pre-existing issues on lines the PR didn't touch.
- Looks like a bug but isn't.
- Anything a linter, typechecker, formatter, or compiler catches.
- Issues a standards doc names but the code explicitly silences (e.g. a lint-ignore with reason).
- Functionality changes that are clearly intentional, part of the broader change.

## No silent truncation

If you drop borderline findings, say so in one line during aggregation — "dropped 3 below threshold" — so the user knows the filter ran, not that the code was spotless.
