# Architecture axis brief

You are one axis of a multi-axis code review. Apply the lens of the `/improve-codebase-architecture` skill to the **changed code only**.

- Diff: `{diff command}`
- Commits: `{commit list}`

**Read the `/improve-codebase-architecture` skill first and use *its* definitions — don't work from memory.** It is the single source of truth for this lens, so this brief doesn't restate it:

- `SKILL.md` — the glossary (module, interface, depth, seam, locality, leverage), the **deletion test**, and the friction questions in its "Explore" step. Look for **deepening opportunities** in the diff: shallow modules the change introduces, a concept decided two different ways across the diff, leaky seams the change widens.
- `LANGUAGE.md` — full definitions and principles; use this vocabulary exactly.
- `DEEPENING.md` — how a deepening would actually be done (dependency categories, seam discipline) so your proposed fix is grounded.

Also read `CONTEXT.md` and any ADRs in the touched area, and use that domain vocabulary alongside the skill's architecture vocabulary. For each finding: name the files, the friction, and a plain-English fix described in terms of **locality** and **leverage**. Respect PR scope — prefer fixes proportionate to the change; flag larger refactors as non-blocking. Don't re-litigate decisions recorded in ADRs unless the friction is real enough to reopen one.

First read [_contract.md](_contract.md) and follow it for report length and finding format.
