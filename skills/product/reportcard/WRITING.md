# Writing the draft

## Branch — created at the first write, not at launch

The audit prints the conventional name as `branch:`
(`<product>-q<n>-<year>-report-card`). Running this skill is not a commitment
to change anything, so a read-only question must not leave a branch behind.

Create it immediately before the first write. If the PM replies and nothing
gets written ("hold off", or every answer is "skip"), no branch. A partial
draft containing `TBC` is a write, so it does get one.

```bash
git switch -c <branch>          # only if it does not already exist
```

Already on that branch, or on a non-`main` branch the PM is clearly using?
Stay there. Otherwise act on what the audit reported:

| Audit says | Do |
| --- | --- |
| `exists locally` | Switch to it, keep going |
| `exists on REMOTE only` | **Stop and ask.** Someone else likely started this quarter |
| `not found` | Create it here |
| `git unavailable` | Carry on, and say the branch step was skipped |

## Appending

New entry keyed by `startDate: 'YYYY-MM-01'`, month `01`/`04`/`07`/`10`.

- Match surrounding style exactly — indentation, date quoting, decimal places.
- `team.members`: omit the block entirely to carry the roster forward. Add one
  only if it actually changed.
- `cost.values`: all six keys — `infra`, `security`, `manpower`, `corporate`,
  `tools`, `others`.
- `CHANGELOG.md`: **not this skill's job** — a good entry needs a scan of
  Slack, GitHub and the team's planning doc, which is out of scope here.
  - If the PM supplies changelog text directly, add it at the top as
    `## Q<n> <year> <Mon-Mon>`, matching the previous entry's structure.
  - If they do not, leave the file alone and say the quarter is missing an
    entry. Do not improvise one from the metric values — numbers are not a
    story.

## When the cost figures are not in yet

**A quarter exists only if it has a `cost.values` entry.** The quarter
dropdown is built from `cost.values` keys alone
(`src/app/services/calculate-costs.ts`); metrics do not contribute. Add
metrics without a cost entry and the page silently keeps showing the previous
quarter — no error, nothing to notice.

So cost blocks *preview*, never *progress*:

1. Write the metrics as normal.
2. Add the cost entry with zeros so the quarter renders, and say plainly that
   you have done so.
3. Open the PR as a **draft**, with `cost figures are placeholder zeros` in
   the description as the one outstanding item.

A draft carrying zeros is normal — it is what makes the quarter previewable.
**Approval is the gate:** reviewers do not approve until the real figures land
in a follow-up commit.

The danger is silence, not the zeros. On the public chart a `0` reads as
"spending collapsed to nothing" rather than "not known yet", so an unflagged
draft can be approved by someone assuming the numbers are real.
