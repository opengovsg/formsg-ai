---
name: highlights
description: Scan a product's Slack channel, GitHub repo and Notion pages for a quarter's shipped work, then draft a CHANGELOG.md entry in that product's existing format. Use when someone wants to write or draft quarterly highlights, gather what shipped last quarter, update a product CHANGELOG, or asks what to put in the changelog for Q1/Q2/Q3/Q4.
---

# Quarterly highlights

Gather what a product shipped in a quarter, decide the few things worth
publishing, and draft the `CHANGELOG.md` entry.

Does not touch `reportcard.yml` — that is `/reportcard`'s job. **Never invent a
metric, a date, or a feature.** Everything published must trace to something a
person actually wrote. A fabricated usage number on a public government page is
the worst outcome available here, and plausible numbers are the easiest thing
to generate by accident.

## 1. Prep

```bash
python3 scripts/prep.py <product> [--quarter q2-2026]
```

Prints the date range, the heading to add, and **the last entry verbatim** —
that is the format to mirror. Do not impose a house style; every product
formats differently and the file is the source of truth. It also lists the
metric labels that product uses (`Usage`, `Ease of use`, …).

## 2. Confirm the sources

Sources differ per product and are not recorded anywhere, so ask — but arrive
with guesses rather than a blank question:

- **GitHub** — try `gh repo view opengovsg/<Product>` and propose it if it exists
- **Slack** — search for a channel matching the product or its division
- **Notion** — ask; there is rarely a way to guess

Ask once, in one message, then confirm before scanning. Also ask if anything
lives elsewhere — a Jira board, a team wiki, a mailing list.

Worth knowing: teams often post through a **weekly digest bot** rather than
individually. Ask how updates usually reach the channel; it changes what to
search for.

## 3. Fan out — one subagent per source

Retrieval is mechanical, so run it in parallel on a cheaper tier and keep the
raw volume out of the main context. Each subagent gets the date range and
returns **raw findings only** — no judgment about importance:

- date, one-line description in the author's own words, link, any hard numbers
- an explicit "could not access X, because Y" rather than silence

Tell each one plainly: do not infer, do not fill gaps, accuracy over
completeness.

## 4. Curate

This is the step that cannot be parallelised — you cannot tell which items
matter until every source is visible at once. See
[CURATING.md](CURATING.md) for how to rank and what to cut.

## 5. Draft

Mirror the previous entry's structure exactly, down to the group names and
metric labels. Where a feature carried a metric last quarter and this
quarter's number is unknown, write:

```
      - Usage: [Placeholder — Q1 reported 6.6k]
```

Quoting last quarter's value gives the PM a baseline — a number that has gone
flat after a feature left beta is worth noticing before it is published.

Write the draft to `.scratch/<product>-<quarter>-changelog-draft.md` for review.
Only paste it into `CHANGELOG.md` once the PM has filled or accepted the
placeholders.

## Model

Opus, high effort, for curation — choosing 10 items from 300 is judgment, not
retrieval. The fan-out subagents can run on Sonnet at medium.
