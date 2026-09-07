---
name: concise-review
description: Review a PR and report it as terse technical bullets — one anchored line per finding, no prose.
disable-model-invocation: true
---

# Concise review

Review the PR named in the arguments and report it under a fixed **output contract**: one anchored bullet per finding, technical register, nothing else on the page.

The review pass here is single-agent and deliberately thin — the four-axis parallel treatment lives in [`/review`](../review/SKILL.md). What this skill owns is the **write-up**.

The register is **commit-message voice**: name the symbol, state what breaks. Every bullet reads like a line in a bug tracker, not a message to a colleague.

## Process

### 1. Pin the target

The argument is a PR number, a PR URL, `owner/repo#n`, or absent.

- **Argument present** → `gh pr diff <arg>` for the diff, `gh pr view <arg> --json number,baseRefName,headRefOid,url` for the coordinates.
- **Absent** → the PR for the current branch. No PR → `git diff <default-branch>...HEAD` (three-dot, against the merge-base), with the default branch from `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.

The diff is the review target. Commit messages, the PR title and description, and branch names are context — every finding is grounded in changed code.

### 2. Find and gate

One pass over the diff. Read the surrounding file whenever the diff alone doesn't settle whether something actually breaks.

Then gate every candidate through [`../review/FILTER.md`](../review/FILTER.md): score it 0–100, drop below 70, and drop the always-false-positive list outright. Keep the drop count — the report states it.

### 3. Write it up

The shape, exactly:

```
3 findings, 2 dropped

- `src/amount.ts:42` [blocking] `parseAmount` returns NaN on an empty string; the guard below treats NaN as 0.
- `src/queue.ts:88` [blocking] `flush` is awaited inside the loop, so a slow batch stalls every later batch.
- `src/queue.ts:12` [nit] `retries` is unused since the retry moved into `fetchWithBackoff`.
```

Rules:

- **One bullet per finding**, one line each, at most 25 words. Whole report at most 200 words. More findings than fit → keep the highest-severity ones and say how many were held back.
- **Anchor every bullet** to `file:line`. A finding that spans the diff anchors to its most relevant changed line; a genuinely diffuse one takes `[cross-cutting]` in the tag slot and no line.
- **Tag severity in one token**: `[blocking]`, `[nit]`, `[question]`, `[cross-cutting]`.
- **State the mechanism and the consequence** — what the code does, and what breaks as a result.
- **Project words only.** Symbols and paths spelled exactly as the diff spells them; domain terms from `CONTEXT.md`. No coined labels.
- **A fix shorter as code goes as code** — a fenced snippet under the bullet, no sentence wrapping it.
- **Label an unverified claim once**: `unverified:` then the claim.
- **Clean is a result**: `0 findings, M dropped` plus one line naming what was checked. Never manufacture nits.

The page carries the counts line and the bullets. Everything else stays off it: no preamble, no restatement of what the PR does, no closing summary, no offer of next steps.

Words to strike, and what goes in their place:

| Strike | Write |
|---|---|
| great work, nice, solid PR, LGTM | nothing — praise is not a finding |
| it's worth noting that, I think we could possibly | the claim, once |
| leverage, utilise | use |
| robust, seamless, elegant, clean | the property that holds: `retries on 5xx`, `no allocation in the loop` |
| crucial, critical, significant, key | the consequence: `drops the last batch` |
| ensure, facilitate, delve into, holistic | check, let, read |
| emoji, exclamation marks | nothing |

### 4. Audit the draft

Check the draft line by line and rewrite until each of these passes:

- Every bullet carries a `file:line` or the `[cross-cutting]` tag.
- Every bullet is one line of at most 25 words; the report is at most 200 words.
- Zero words from the strike table, zero praise, zero stacked hedges.
- Every sentence says what is wrong, not what the PR does.
- The counts line matches the bullets, the drop count, and anything held back.

Report only once the draft passes clean.

### 5. Post to the PR, if asked

Only on request. Post one batched inline review — head SHA, payload shape, the unchanged-line 422, re-review delta, and skipping closed/merged/draft PRs all live in [`../review/COMMENTS.md`](../review/COMMENTS.md).

Each comment body keeps **this** skill's contract: one anchored line, severity tag, snippet if the fix is code. No sections, no confidence score. The AI disclaimer from `COMMENTS.md` stays.
