# PR Body Template

Voice for every filled section: a teammate who knows the product, not the
spec. Matter-of-fact STE (ASD-STE100). Terms from `CONTEXT.md`. Sources feed
**you**; the body carries their **meaning** in plain prose — never their
labels (`D10`, `§A0`, `S6`, …).

Section order is fixed. Omit any sub-section whose source is empty — no
"N/A", no placeholder.

## Template

```md
## Problem

<2–4 STE sentences in CONTEXT.md terms. Name the user-visible problem a product teammate already recognizes. End with "Closes <ticket-ref>" when a ticket exists.>

## Solution

<One short STE paragraph at standup level: what changed and why it solves the Problem. Translate breadcrumbs, ADRs and the spec into product language a teammate can act on without opening those sources — e.g. "cap retries when the gateway times out", not `D10` / `§A0` / `S6`. Use ### only for genuinely separate facets (e.g. ### Feature flagging, ### Migration).>

**Alternatives considered**
<One conversational STE bullet per breadcrumb (kind: pr-body) or rejected ADR option: "We considered X, but skipped it because Y." Reader knows the product; explain the deliberation. Omit when both sources are empty.>

**Breaking Changes**

<One line: "No - backwards compatible." or "Yes - <what breaks> + <migration step>".>

## Tests

<Manual scenarios a human reviewer must run by hand (omit tests covered by code tests). All checkboxes unchecked — reviewer TODO, not author runs. One **TC** per distinct scenario; steps a teammate can follow without the spec.>

**TC1: <scenario>**

- [ ] <step>
- [ ] <step>

**TC2: <scenario>**

- [ ] <step>
```

GitHub's Commits tab covers the commit list — do not add a
Review guide section.

## Sourcing the Tests section

- Prefer the spec's own Tests block when it is already in this TC-grouped shape.
- Otherwise build TCs from the spec or ticket user-journey or acceptance-criteria sections — one TC per distinct scenario.
- If the spec has no testable scenarios (rare — pure docs PRs), omit the section.
