# Finding contract (shared by all axes)

Every axis brief follows this. It's the single source of truth for report length and finding format — the filter in `SKILL.md` step 5 relies on it, so don't restate it per brief.

**Scope — code only.** Review the code in the diff. Commit messages, commit/PR titles and descriptions, and branch names are **context, not review targets** — never raise a finding about them, even when a standards doc documents a commit-message or PR convention. Every finding must be grounded in the changed code (anchored to a line on a best-effort basis — see below).

**Length:** keep your whole report **under ~400 words**. A short list of verified, located findings beats a long list of maybes — do not pad.

**For each finding:**

- Anchor to a `file:line` and quote the line(s) of code it concerns. **Anchoring is the default, not optional:** every finding must name the specific changed line it sits on so it can be posted inline. A finding that *genuinely* spans the change still anchors to the most relevant changed line and explains the broader scope in its text — it does **not** get to skip a line. The only findings without a single anchor are the truly diffuse ones (a pattern across many files, a concern about the shape of the diff); flag those explicitly as cross-cutting with a one-line reason there's no single line. "Best-effort" means pick the best line when one isn't perfect — never license to drop the anchor or lump findings into one unanchored blob.
- **Disposition depends on your axis-type**, plus one line of evidence either way:
  - **Standards / Spec (correctness):** state a confidence (0–100) that it's a real, in-scope issue.
  - **Architecture / Divergent (judgement):** no number — state instead whether the reasoning holds and the alternative is genuinely better for the PR's scope. Don't invent a score; that disposition *is* your gate (see your brief).
- Cross-cutting findings cite a primary `file:line` plus the others.