# PR Body Template

The body must be **concise**. Reviewers skim — long bodies get ignored. Prefer plain language; the project's `CONTEXT.md` is the canonical glossary for terms.

Section order is fixed. Any sub-section whose source is empty is **omitted entirely** — no "N/A", no placeholder.

## Template

```md
## Problem

<2–4 sentences from the PRD/issue. End with "Closes <issue-ref>" if one exists.>

## Solution

<Short prose paragraph — what changed and why, at a teammate-explaining-it-in-standup level. Use ### sub-headings only when the change has genuinely separate facets (e.g. ### Feature flagging, ### Migration).>

**Alternatives considered**
<Plain conversational English — "We considered X, but skipped it because Y" — not terse "X: rejected — Y" shorthand. Assume the reader knows the product but not the deliberation. One bullet per breadcrumb (kind: pr-body) or rejected ADR option. Omit if both sources are empty.>

**Breaking Changes**

<One line. "No - backwards compatible." or "Yes - <what breaks> + <migration step>".>

## Tests

<Manual test cases only — anything a human reviewer/QA must run by hand. Omit anything covered by CI. All checkboxes unchecked; the section is a reviewer TODO, not a record of author runs.>

**TC1: <scenario>**

- [ ] <step>
- [ ] <step>

**TC2: <scenario>**

- [ ] <step>
```

The Review guide section (commit list) is **intentionally omitted** — GitHub's Commits tab already does this.

## Sourcing the Tests section

- Prefer the PRD's own Tests block if it is already in this TC-grouped shape.
- Otherwise build TCs from the PRD/issue's user-journey or acceptance-criteria sections, one TC per distinct scenario.
- If the PRD has no testable scenarios (rare — pure docs PRs), omit the section.

## Length budget

Aim for the whole body to fit on one screen without scrolling on a 13-inch laptop. If overrun, the Solution paragraph is the first thing to cut — the diff already shows the *what*.
