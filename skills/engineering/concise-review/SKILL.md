---
name: concise-review
description: Review a PR and report it as one flat list of concise bullet points — no headings, no grouping.
disable-model-invocation: true
---

# Concise review

Review the PR named in the arguments and report it under a fixed **output contract**: one flat list of plain bullets, and nothing else.

The review pass here is single-agent and deliberately thin — the four-axis parallel treatment lives in [`/review`](../review/SKILL.md). What this skill owns is the **write-up**.

The register is **changelog voice**: name the thing, say what happens. One plain sentence per finding, the kind a colleague says pointing at a line.

**The contract governs the whole reply**, not a block inside it. The first character of the reply is the first bullet's `-`, and the reply ends at the last bullet — no preamble, no reasoning, no offer of next steps. A dry run prints the list and stops.

## Process

### 1. Pin the target

The argument is a PR number, a PR URL, `owner/repo#n`, or absent.

- **Argument present** → `gh pr diff <arg>` for the diff, `gh pr view <arg> --json number,baseRefName,headRefOid,url` for the coordinates.
- **Absent** → the PR for the current branch. No PR → `git diff <default-branch>...HEAD` (three-dot, against the merge-base), with the default branch from `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.

The diff is the review target. Commit messages, the PR title and description, and branch names are context — every finding is grounded in changed code.

### 2. Find and gate

One pass over the diff. Read the surrounding file whenever the diff alone doesn't settle whether something actually breaks.

Then gate every candidate through [`../review/FILTER.md`](../review/FILTER.md): score it 0–100, drop below 70, and drop the always-false-positive list outright. Keep the drop count — the last bullet states it.

### 3. Write it up

The shape, exactly:

```md
- `parseAmount` returns NaN for an empty string, so the guard below saves it as zero. — `src/amount.ts:42`
- `flush` is awaited inside the loop, so one slow batch stalls every batch behind it. — `src/queue.ts:88`
- `retries` is unused since the retry moved into `fetchWithBackoff`. — `src/queue.ts:12`
- Is the 30s timeout deliberate? The gateway gives up at 10s. — `src/client.ts:55`
- 11 files reviewed, 6 candidates dropped below the confidence gate.
```

Rules:

- **One flat list.** No headings, no grouping, no sub-lists, no severity tags, no table, no counts line above it.
- **Order carries severity** — what breaks first, what is merely real after it, questions last. Nothing labels it.
- **One idea per bullet**, one line, one clause, at most 20 words. Whole list at most 15 bullets.
- **Anchor at the end** — `— \`file:line\``, after the sentence, so the sentence leads. A finding spanning the diff anchors to its most relevant changed line; a genuinely diffuse one ends `— cross-cutting`.
- **Say the mechanism and the consequence** — what the code does, and what breaks because of it.
- **A semicolon joining two findings is two bullets.**
- **The last bullet is always coverage** — how much was reviewed and how many candidates were dropped. It is the only bullet without an anchor.
- **Nothing found is a result**: the coverage bullet alone, plus one bullet naming what was checked. Never manufacture nits.
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

- Every line of the reply starts with `- `. No heading, no blank-line-separated group, no sentence outside a bullet.
- Every bullet is one line, one clause, at most 20 words, and ends in an anchor — except the last, which is coverage.
- Bullets run most severe first.
- Every bullet says what is wrong, not what the PR does.
- Zero words from the strike table, zero praise, zero stacked hedges, zero severity tags.
- The reply's first character is `-` and its last character ends the final bullet.

Report only once the draft passes clean.

### 5. Post to the PR, if asked

Only on request. Post one batched inline review — head SHA, payload shape, the unchanged-line 422, re-review delta, and skipping closed/merged/draft PRs all live in [`../review/COMMENTS.md`](../review/COMMENTS.md).

Each comment body is the bullet's sentence and nothing else — no bullet marker, no heading, no severity label, no confidence score. GitHub anchors the comment, so drop the trailing `— file:line`. The coverage bullet goes in the review summary, not on a line. The AI disclaimer from `COMMENTS.md` stays.
