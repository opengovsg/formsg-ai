# Posting findings as PR comments

Only when the user asks to post to the PR. A surviving finding (one that passes the gate in [FILTER.md](FILTER.md)) becomes a comment. The goal is **mental alignment with the author** — they should finish reading and understand the change you'd make and *why*, without re-deriving it.

## Where to post

**Inline, on the line(s), is mandatory.** Every finding anchors to the specific changed line it concerns — a line-pinned review comment, not a bottom-of-PR issue comment. On-the-LoC comments are far easier for the author to act on than a wall of prose at the bottom. **Do not use `gh pr comment`** for findings — it posts an unanchored issue comment, which is the failure mode this skill exists to avoid.

### How to post — one batched review

Post all findings as a **single review** via the GitHub review API, with one entry in the `comments[]` array per finding. One atomic call, one notification, every finding inline. Build it in three steps:

1. **Resolve the head SHA and repo/PR coordinates:**
   ```bash
   gh pr view <pr> --json number,headRefOid,headRepository,headRepositoryOwner \
     -q '{n: .number, sha: .headRefOid}'
   # owner/repo: gh repo view --json owner,name -q '.owner.login + "/" + .name'
   ```
2. **Assemble the review payload** — `event: COMMENT`, an optional `body` (the summary; see below), and a `comments[]` array. Each comment needs `path`, `line` (the line in the file's new version), `side` (`RIGHT` for added/context lines, `LEFT` for deleted), and `body` (the formatted finding). Write it to a temp JSON file so multi-line bodies and arrays stay intact:
   ```bash
   gh api repos/{owner}/{repo}/pulls/{n}/reviews \
     --method POST --input review.json
   ```
   where `review.json` is:
   ```json
   {
     "commit_id": "<headRefOid>",
     "event": "COMMENT",
     "body": "<summary — empty string if none>",
     "comments": [
       { "path": "src/foo.ts", "line": 42, "side": "RIGHT", "body": "issue (standards, confidence: 85/100): ..." },
       { "path": "src/bar.ts", "line": 88, "side": "RIGHT", "body": "suggestion (divergent): ..." }
     ]
   }
   ```
3. **If a comment's line lands on an unchanged line** GitHub rejects the whole review (422). For a finding that spans a hunk, use `start_line` + `line` (range) or pin to the nearest changed line within the hunk and explain the scope in the body — see the cross-cutting rule below.

### Cross-cutting findings → the summary body

A finding that genuinely spans the change (a pattern repeated across files, an architectural concern about the shape of the diff) and has **no single most-relevant line** goes into the review's `body` (the summary), **not** a standalone bottom comment and **not** forced onto an arbitrary line. Each such finding must carry a one-line justification of why it has no single anchor. Everything that *can* be pinned to a line **must** be — don't drain findings into the summary to avoid anchoring work.

### The summary body otherwise

Beyond cross-cutting findings, add summary text only if it adds value: what to focus on first, what the review covered, what it deliberately skipped. Skip it if the inline comments speak for themselves — don't restate them. An empty `body` is fine when every finding is inline.

## When there's nothing to post (empty / low-signal)

A finding-free result is a valid result — never manufacture nits to look busy (the false-positive list in [FILTER.md](FILTER.md) exists to prevent exactly this). If nothing survives the filter, post a single brief summary noting no issues were found and summary of what was checked — and no inline comments. The reviewer is allowed to find nothing.

## Re-reviewing a PR that already has a review

Before posting, check whether this tool already left a review (look for prior `🤖 ...AI code review` comments). If it did, **do not repost** — re-evaluate against what changed since:

1. **Read the prior comments and the author's replies.** If the author pushed back with a load-bearing reason (as in the subpath-export thread — *"happy to keep things consistent"*), treat that thread as resolved; don't re-raise it.
2. **Read the commits pushed since the last review.** A finding the author has since fixed is resolved — confirm the fix rather than re-flagging it; resolving reply is enough.
3. **Post only the delta:** genuinely new findings introduced by the new commits, and follow-ups on prior comments that are still unaddressed *and* weren't reasonably declined.

Skip entirely if the PR is closed, merged, or draft.

## Conventional comments

Follow the Conventional comments spec. Avoid `praise` to reduce noise.

### Show the confidence score (correctness axes only)

Name the **axis** in the decoration slot so the author can place the finding at a glance, and surface the `confidence` (0–100) for correctness findings so they can weigh it:

- Standards and Spec findings carry a numeric `confidence` from the filter — `<axis>, confidence: NN/100`, using the axis name (`standards` / `spec`).
- Architecture and Divergent findings have **no** numeric score (their disposition is "the reasoning holds and the alternative is genuinely better") — name the axis alone (`architecture` / `divergent`), don't invent a score.

Place the score as the **last item in the Conventional-Comments decoration slot**, after any other items.

- no other decoration: `issue (standards, confidence: 85/100): ...`
- with decoration(s): `suggestion (non-blocking, spec, confidence: 90/100): ...`
- multiple decorators: `issue (blocking, if-minor, standards, confidence: 100/100): ...`
- divergent or architecture axis: `suggestion (divergent): ...` (axis named, no confidence)

Surviving correctness findings sit above the cutoff [FILTER.md](FILTER.md) sets (the filter drops the rest), so the number is a confidence signal to prevent false positives.

## Combine similar comments 

Don't bury the author in dozens of tiny comments — batch the same issue across the diff into one comment (with a patch/snippet where it helps). One `polish:` covering every `m_x → x` rename beats twenty.

## AI disclaimer

End each comment (or the summary, if findings are grouped under it) with:

> 🤖 This comment was generated by an AI code review. Please verify before acting on it.

## Prioritise making comments as humanly readable.

A wall of prose makes a comment hard to understand.

### Use the project's words, not new ones

Mental alignment depends on shared vocabulary, so name things with terms the author already knows — not a label you coined for this comment.

- **Reuse the project's domain language.** If `CONTEXT.md` calls it the "Order intake module," call it that — not "the `FooBarHandler`" or "the order service."
- **No invented jargon.** If a concept genuinely has no name, describe it in common simple words rather than minting a term the author has to decode. Avoid abstract reviewer-speak ("altitude", "leverage the synergy", "at a high level") — say the concrete thing simply for a junior engineer.
- **Match the codebase's own names.** Refer to symbols, files, and concepts by exactly the names they carry in the diff.

### Use common and simple words
> Bad: issue (non-blocking): building on the now-resolved split disposition — this new judgement track asks the verifier to decide whether "the reasoning holds and the alternative is genuinely better," but that verifier still runs on Haiku (line 7).
This is not ideal as it uses uncommon words eg, `now-resolved split disposition` and uses quotes "the reasoning holds and the alternative is genuinely better" which are painful to understand. 

> Good: issue (non-blocking): verification for the judgement track uses a weaker model leading to poor performance; we should conditionally use a stronger model instead.

The only exception for using challenging words is if it is part of the project's vocabulary. 

### Use sections

Potential sections to use, only if the finding needs them: **What's happening** (the observation) · **Why it bites later** (the cost) · **Suggestion** (the concrete change) · **Context** (the existing pattern/precedent) · **Benefits** (a bullet list when there's more than one). 

Example of improving readability with sections:

**Without sections** (one unbroken paragraph, very painful to understand):

> Architectural suggestion: expose the adapters via a subpath export instead of decorating the factory function. This loop copies named exports onto the default factory function so CJS consumers can reach adaptV3ToV4 / adaptV4ToV3. It works, but it's a workaround for overloading one entry point with two unrelated responsibilities… [six more sentences] …prefer explicit named assignments over the dynamic loop so the export surface is legible.

**With sections**:

> **suggestion:** instead of a loop copying named exports onto the default factory function so CJS consumers (the backend) can reach `adaptV3ToV4` / `adaptV4ToV3`, shall we use the existing `packages/sdk/package.json` subpath-export approach to keep things consistent?
>
> **Context:** `"./dist/types"` hit the same issue and was resolved with a subpath export, as in our `formsg-shared` package.
>
> **Suggested addition:**
> ```json
> "./adapters": {
>   "import":  { "types": "./dist/esm/adapters.d.ts", "default": "./dist/esm/adapters.js" },
>   "require": { "types": "./dist/cjs/adapters.d.ts", "default": "./dist/cjs/adapters.js" }
> }
> ```
> **Benefits:**
> - Avoids a named export silently colliding with an intrinsic function property (`name`, `length`) — fine for today's names, a risk as the surface grows.
> - Keeps one method in the codebase for resolving these exports.
>
> 🤖 This comment was generated by an AI code review. Please verify before acting on it.

### Use bullet points

Break up long sentences and lists (alternatives, benefits, trade-offs) with concise bullet points. 

**Bad**, since it uses quotes which are hard to comprehend and should use simple plain english instead:
Suggestion: route verification by axis-type — keep Haiku for the correctness axes (Standards/Spec) as designed, but verify the judgement axes (Architecture/Divergent) on the review model, or skip independent verification for them and lean on "surface the strongest few." A one-line split by axis-type closes the gap the new disposition opened.

**Good**: 
Suggested Fix: Use different models based on the axis-type. For: 
- Correctness axes (Standards/Spec): Keep these on Haiku. 
- Judgement axes (Architecture/Divergent): Use a stronger model (recommending the same model as the main /review agent) to improve performance. 
Otherwise, consider trusting the original model's output and show the highest confidence findings to the user.

This good example uses plain simple english and bullet points to make it more readable. 
