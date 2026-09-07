---
name: concise-review
description: Review a PR and report it as simple bullets under Blocking, Non-blocking, Questions, and Checked.
disable-model-invocation: true
---

# Concise review

Review the PR named in the arguments and report it under a fixed **output contract**: four headings, flat bullets, nothing else.

The review pass here is single-agent and deliberately thin — the four-axis parallel treatment lives in [`/review`](../review/SKILL.md). What this skill owns is the **write-up**.

The register is **changelog voice**: name the thing, say what happens. One plain sentence per finding, the kind a colleague says pointing at a line.

**The contract governs the whole reply**, not a block inside it. Nothing before the first heading, nothing after the last bullet — no preamble, no reasoning, no offer of next steps. A dry run prints the report and stops.

## Process

### 1. Pin the target

The argument is a PR number, a PR URL, `owner/repo#n`, or absent.

- **Argument present** → `gh pr diff <arg>` for the diff, `gh pr view <arg> --json number,baseRefName,headRefOid,url` for the coordinates.
- **Absent** → the PR for the current branch. No PR → `git diff <default-branch>...HEAD` (three-dot, against the merge-base), with the default branch from `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.

The diff is the review target. Commit messages, the PR title and description, and branch names are context — every finding is grounded in changed code.

### 2. Find and gate

One pass over the diff. Read the surrounding file whenever the diff alone doesn't settle whether something actually breaks.

Then gate every candidate through [`../review/FILTER.md`](../review/FILTER.md): score it 0–100, drop below 70, and drop the always-false-positive list outright. Keep the drop count — `## Checked` states it.

### 3. Write it up

The shape, exactly:

```md
## Blocking

- `parseAmount` returns NaN for an empty string, so the guard below saves it as zero. — `src/amount.ts:42`
- `flush` is awaited inside the loop, so one slow batch stalls every batch behind it. — `src/queue.ts:88`

## Non-blocking

- `retries` is unused since the retry moved into `fetchWithBackoff`. — `src/queue.ts:12`

## Questions

- Is the 30s timeout deliberate? The gateway gives up at 10s. — `src/client.ts:55`

## Checked

- 11 changed files, 6 candidates dropped below the confidence gate.
- The flag-off path and the existing save row are unchanged.
```

Rules:

- **One idea per bullet**, one line, at most 20 words. Whole report at most 250 words.
- **Headings are fixed and ordered** — Blocking, Non-blocking, Questions, Checked. Omit any heading with no bullets, except `## Checked`, which is always present.
- **Severity is the heading**, never a tag inside the bullet. `Blocking` breaks something; `Non-blocking` is real but survivable; `Questions` is where you need the author to answer.
- **One clause per bullet.** A semicolon joining two findings is two bullets.
- **Anchor at the end** — `— \`file:line\``, after the sentence, so the sentence leads. A finding spanning the diff anchors to its most relevant changed line; a genuinely diffuse one ends `— cross-cutting`.
- **Say the mechanism and the consequence** — what the code does, and what breaks because of it.
- **`## Checked` carries the drop count** and one line per area confirmed clean. Nothing found is a result: the heading still appears, with the count and what was covered. Never manufacture nits.
- **Project words only.** Symbols and paths spelled exactly as the diff spells them; domain terms from `CONTEXT.md`. No coined labels.
- **A fix shorter as code goes as code** — a fenced snippet under the bullet, no sentence wrapping it.
- **Label an unverified claim once**: `unverified:` then the claim.

Words to strike, and what goes in their place:

| Strike | Write |
|---|---|
| great work, nice, solid PR, LGTM | nothing — praise is not a finding |
| it's worth noting that, I think we could possibly | the claim, once |
| leverage, utilise | use |
| robust, seamless, elegant, clean | the property that holds: `retries on 5xx` |
| crucial, critical, significant, key | the consequence: `drops the last batch` |
| ensure, facilitate, delve into, holistic | check, let, read |
| emoji, exclamation marks | nothing |

### 4. Audit the draft

Check the draft line by line and rewrite until each of these passes:

- Headings are Blocking, Non-blocking, Questions, Checked, in that order, and each one present carries at least one bullet.
- `## Checked` is present, and its count matches the bullets above it and anything held back.
- Every bullet is one line of at most 20 words, one clause, ending in an anchor.
- Every bullet says what is wrong, not what the PR does.
- Zero words from the strike table, zero praise, zero stacked hedges.
- The reply starts at `## Blocking` (or the first non-empty heading) and ends at the last bullet — nothing wrapped around it.

Report only once the draft passes clean.

### 5. Post to the PR, if asked

Only on request. Post one batched inline review — head SHA, payload shape, the unchanged-line 422, re-review delta, and skipping closed/merged/draft PRs all live in [`../review/COMMENTS.md`](../review/COMMENTS.md).

Each comment body keeps **this** skill's voice: one plain sentence, no heading, no confidence score. GitHub anchors the comment, so drop the trailing `— file:line` and lead with the severity the heading carried — `Blocking:`, `Non-blocking:`, or `Question:`. The AI disclaimer from `COMMENTS.md` stays.
