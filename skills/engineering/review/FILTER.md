# False-positive filter

Adapted from Anthropic's `/code-review`. Findings the user dismisses cost more credibility than findings you miss. Every finding from every axis passes through this before aggregation.

## How to run it

**One verifier per finding, in parallel — routed by axis-type.** Each gets only the diff, the one finding, and the standards-file list — **not** the originating axis's reasoning (the finder is the worst judge of its own finding).

- **Correctness axes (Standards/Spec)** → verify on **Haiku** (`Agent(..., model: "haiku")`; in a Workflow, `agent(prompt, {model: "haiku"})`). Locating a bug against the rubric is cheap, and stays cheap only because it's Haiku + single-finding + parallel — don't hand one agent all findings.
- **Judgement axes (Architecture/Divergent)** → verify on **the review model**.

The verifier:

1. **Locates the finding** via its cited `file:line` + quoted code — best-effort: an off-by-a-few line or a cross-cutting finding still counts as located if its quoted code is in the diff. Score **0** only when the finding can't be tied to the changed code at all (the quote matches nothing) — that's the unfalsifiable, likely-hallucinated case the gate exists to catch.
2. For a finding against a documented standard, **confirms the doc actually says it** — "CLAUDE.md says so" doesn't count if the rule isn't there.
3. **Applies the track for its axis** (see Disposition): Standards/Spec → a 0–100 confidence score against the rubric; Architecture/Divergent → whether the *reasoning holds and the alternative is genuinely better*. Returns its verdict + one line of evidence.

### Dedup

Per-finding verifiers can't see each other, so the same file+line flagged by two axes (commonly Architecture **and** Divergent) survives twice. After scoring, the orchestrator merges them — highest score, cite both axes. A text-merge, not another agent.

### Rubric (correctness axes — give to the scoring agent verbatim)

- **0** — False positive that doesn't survive light scrutiny, or a pre-existing issue.
- **25** — Might be real, couldn't verify; if stylistic, not named in a standards doc.
- **50** — Verified real, but a nitpick or rare in practice.
- **75** — Double-checked; likely hit in practice, or directly named in a standards doc.
- **100** — Evidence confirms a real issue that will happen frequently.

### Disposition — an 80 doesn't mean the same thing on every axis

The rubric is calibrated for *bug-likelihood*, so a single cutoff would filter out the design feedback this skill exists to surface:

- **Standards & Spec (correctness):** the finding claims something is *wrong* → **drop everything below 80**.
- **Architecture & Divergent (judgement):** no numeric cutoff — keep a finding only if the *reasoning holds and the alternative is genuinely better* for the PR's scope. Surface the strongest few.

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
