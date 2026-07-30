---
name: reportcard
description: Add a new quarter's team, cost and metric values to an OGP product report card (_products/<product>/reportcard.yml) by auditing the last recorded quarter, then asking the PM for each missing number. Use when someone wants to update, add, or draft a quarterly report card, add a new quarter's metrics/cost/team, or mentions reportcard.yml, "Q1/Q2/Q3/Q4 report card", or the products.open.gov.sg draft editor. Writing the CHANGELOG entry is out of scope for this skill.
---

# Report card: add a quarter

Collect a quarter's numbers from the PM and append them to
`_products/<product>/reportcard.yml`.

Does not source data, does not open PRs, and does not write the changelog —
that needs a scan of Slack, GitHub and the team's planning doc, which is
out of scope here. **Never invent, interpolate, or
carry forward a metric value** — every number comes from the PM, anything
unanswered stays `TBC`, and past quarters are never edited.

## 1. Audit — never read the YAML by eye

```bash
python3 scripts/audit.py _products/<product>/reportcard.yml
```

Stdlib only, so it runs before `npm i`. `--quarter 2026-04-01` targets a
specific quarter; otherwise it infers the next one. `--active-only` hides
retired metrics.

It prints the target quarter, the table headers to use, the branch name and
its status, the last roster and cost entry, and sorts every metric into:

| Bucket | Meaning | What to do |
| --- | --- | --- |
| `NEED` | Carried a value last quarter | Ask the PM |
| `auto` | Derived from other fields | Never ask |
| `DORMANT` | No value last quarter | Offer once, then drop |

PMs retire metrics all the time, so a quiet metric is usually a deliberate
choice rather than an oversight. Offer the dormant list once so nothing is
lost silently, accept "skip them", and never raise it again.

Heed the cost warning if it appears — a quarter without a `cost.values` entry
does not render at all.

## 2. Ask

Follow [ASK-FORMAT.md](ASK-FORMAT.md): four tables, then Notes, then a
copy-paste reply block keyed by metric id in file order. Show every last-known
value so the PM can answer with a delta rather than hunting for context.

## 3. Write

Follow [WRITING.md](WRITING.md): branch at the first write, append-only edits,
and what to do when the cost figures have not arrived.

## 4. Verify

```bash
git diff _products/<product>/reportcard.yml
```

**Every hunk must be pure additions.** One deleted line means history was
rewritten instead of appended — stop and fix it. Re-run the audit; every
`NEED` should now read `OK`.

Then have the PM preview at `products.open.gov.sg/draft/<product>` before the
PR. The diff catches structural damage; only the preview catches a plausible
number in the wrong row.

Handing off for review is `prepare-for-review`'s job, not this skill's. Any
screenshot goes in `.scratch/` and is never committed.
