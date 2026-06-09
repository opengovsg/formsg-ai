# Standards axis brief

You are one axis of a multi-axis code review. Review **only** the diff below against the repo's standards.

- Sources to read first: `{standards files}`
- Diff: `{diff command}`
- Commits: `{commit list}`

Two passes:

1. **Documented standards.** Read the standards docs. Then read the diff. Report, per file/hunk, every place the diff violates a documented standard. Cite the standard (file + the exact rule).
2. **De facto standards.** Zoom out — read enough of the surrounding repo to learn the patterns the codebase *actually* follows, even where undocumented. Flag where the diff diverges from them.

**Question the standard before enforcing it.** Prioritise documented standards, but if a documented rule or an established repo pattern is itself a hack, workaround, or clearly incorrect practice, say so rather than holding the diff to it. A standard that is tech debt should be flagged as tech debt, not used as a stick. When the diff *breaks* from a bad pattern deliberately, that's a point in its favour — note it.

Distinguish hard violations from judgement calls. Skip anything a linter, formatter, or typechecker enforces.

First read [_contract.md](_contract.md) and follow it for report length and finding format.
