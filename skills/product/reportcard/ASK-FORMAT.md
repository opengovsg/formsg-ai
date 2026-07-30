# Ask format

How to present the audit to a PM and collect their numbers.

## Output order

**Tables first, prose last.** Four tables back to back, one-line captions
only, then a single Notes block, then the reply block. Never interleave
commentary between tables — it breaks the scan, and the tables are what the
PM is actually reading.

1. One-line header — product and target quarter
2. **Team** table
3. **Cost** table
4. **Metrics** table
5. **Dormant** table (omit if empty)
6. **Notes** (omit if nothing to flag)
7. **Reply block**

Order rows the way `reportcard.yml` orders them — `team`, then `cost` keys,
then metrics in `metricGroups` order, then `changelog`. The audit already
prints them in file order, so the PM can read the file and the ask in step.

## Tables

Every table shows the previous quarter filled and the target quarter blank.
Use **quarter labels as headers, never ISO dates**. The audit prints the exact
pair as `table columns:` — copy it rather than deriving it.

Team:

| Person | Role | Q1 2026 | Q2 2026 |
| --- | --- | --- | --- |
| alex | eng | full | |
| bo | ops | 2/3 | |

Quarter columns hold involvement (`full` when the YAML omits `involvement`).
Blank means carry forward; `-` means the person left. Caption with the quarter
the roster came from, and ask only for the **delta** — "unchanged" is a valid
and common answer. Never render a roster as a prose sentence; it is the
hardest bucket to check by eye.

Cost and Metrics:

| id | Q1 2026 | Q2 2026 |
| --- | --- | --- |
| infra | 12,345.67 | |
| paper-forms-left | 12,000 | |
| cost-per-form-submission-manual | $0.25 | |

Dormant uses `id` + `Last value` + `Quarters missing` — **no target-quarter
column**, since nothing is being collected. Caption it as awareness only, e.g.
"not collected — say the word to revive". It is a record that these once
existed, not a request.

### Formatting values

- Thousands separators and prefixes are for readability only. Write the raw
  number into the YAML.
- Take a prefix **verbatim from the metric's own `prefix` field**. A metric
  with `prefix: '$'` renders as `$0.25`, never `FormSG$0.25`. The product name
  belongs in the header line and nowhere else.
- Use each id exactly as it appears in the file, including odd casing like
  `Uptime`.

## Notes

One bullet per flag, only things that change what the PM should do:

- Roster empty, or carried forward from more than one quarter back
- Cost fields at `0` — real, or a placeholder? `0` renders as a genuine
  datapoint on the public chart
- **Cost gates the whole quarter.** The quarter dropdown is built from
  `cost.values` alone, so until a cost entry exists the new quarter will not
  appear on the page at all. Say so when asking, so the PM knows these six
  numbers unblock everything else
- `CHANGELOG.md` missing intervening quarters
- Dormant metrics — one bullet total, not one per metric

Nothing to flag means no Notes block. Do not pad it.

## Reply block

A PM gathers these numbers from finance, Datadog, and a survey, so they will
answer in pieces. Always end with a copy-paste block keyed by id, in file
order:

```
team: unchanged
infra: 0
security: 0
manpower: 0
corporate: 0
tools: 0
others: 0
paper-forms-left:
cost-per-form-submission-manual:
respondent-satisfaction-rating:
admin-satisfaction-rating:
Uptime:
paper-forms-left-moe-schools:
percentage-forms-converted-schools:
changelog:
```

The `changelog:` line is optional and exists only so a PM who already has the
text can hand it over. Leaving it blank is normal — writing a proper entry
needs a scan of Slack, GitHub and the planning doc, which is out of scope
for this skill. Never write one yourself from the metric values.

**Cost keys are pre-filled with `0`** — not because zero is likely right, but
because a quarter with no cost entry does not render at all. The default gets
the PM to a previewable page without waiting on finance.

Say this when you send the block: *"cost is pre-filled with 0 so the quarter
renders — overwrite with real figures when finance sends them."*

Treat cost as unanswered whenever **all six come back as `0`**. That is the
default echoed back, not a decision, so it means placeholder: draft PR, flagged
in the description. Individual zeros are ordinary — most products genuinely
have `security: 0` — so only the all-zero case is the signal.

**Only `NEED` items appear here.** Never put a dormant metric in the reply
block, not even commented out — a blank line reads as an obligation, and the
whole point of dormant is that the PM owes nothing. Reviving one is opt-in:
they name it explicitly ("bring back officer-satisfaction"), and only then
does it join the block on the next round.

- **Partial is fine.** A blank line is unanswered. Re-ask only the blanks;
  never re-ask what is already filled.
- **Order-independent and unambiguous** — keys are ids, so nothing misaligns
  the way a bare list of numbers does.
- Loose replies are fine too (`total-users 12500`, or one value at a time).
  The block is a convenience, not a required format.

Keep asking in rounds until every line is filled or the PM stops, then write
`TBC` for the rest and list them at the end.
