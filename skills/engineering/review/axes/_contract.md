# Finding contract (shared by all axes)

Every axis brief follows this. It's the single source of truth for report length and finding format — the filter in `SKILL.md` step 5 relies on it, so don't restate it per brief.

**Scope — code only.** Review the code in the diff. Commit messages, commit/PR titles and descriptions, and branch names are **context, not review targets** — never raise a finding about them, even when a standards doc documents a commit-message or PR convention. Every finding must be grounded in the changed code (anchored to a line on a best-effort basis — see below).

**Length:** keep your whole report **under ~400 words**. A short list of verified, located findings beats a long list of maybes — do not pad.

**For each finding:**

- Anchor to a `file:line` and quote the line(s) of code it concerns. **Best-effort:** always try to pin a finding to a specific line, but a real finding that genuinely spans the change rather than sitting on one line should anchor to the most relevant changed line and say so — don't drop it just because one line doesn't capture it.
- State your confidence (0–100) that it's a real, in-scope issue, plus one line of evidence.
- Cross-cutting findings cite a primary `file:line` plus the others.