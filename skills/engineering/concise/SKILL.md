---
name: concise
description: Write PR bodies and PR comment replies as concise, human-readable bullets — the repo's own PR template, filled with plain sentences.
disable-model-invocation: true
---

# Concise

Write about a PR — its body, or a reply to its comments — under a fixed **voice contract**: short bullets a teammate reads once and acts on.

Two modes, one voice:

| Mode | Trigger | Output |
|---|---|---|
| **Body** | `/concise` on a branch or PR, or `/concise <pr>` | The PR description, shaped by the repo's PR template |
| **Reply** | `/concise reply`, or a PR with unanswered comments named in the arguments | One reply per open comment thread |

What this skill owns is the **write-up**. Breadcrumb, ADR and spec sourcing lives in [`/prepare-for-review`](../prepare-for-review/SKILL.md); finding issues lives in [`/review`](../review/SKILL.md); slicing lives in [`/split-prs`](../split-prs/SKILL.md).

Runs in any repo. `docs/agents/` and breadcrumbs sharpen the output when they exist; nothing here requires them.

## The voice contract

The register is **changelog voice**: name the thing, say what it does. Every bullet reads like a line in a release note, not a paragraph explaining itself.

- **One idea per bullet**, one line, at most 20 words. A semicolon joining two ideas is two bullets.
- **Say the mechanism and the consequence** — what the code does, and what follows from it.
- **Project words only** — domain terms from `CONTEXT.md`, symbols and paths spelled exactly as the diff spells them. No coined labels.
- **A claim the diff cannot support, and no source confirms, does not go on the page.** State inferred rationale as inference.
- **A fix shorter as code goes as code** — a fenced snippet, no sentence wrapping it.
- **No praise, no preamble, no closing summary, no offer of next steps.**

**The contract governs the whole reply**, not a block inside it. A dry run prints the text and stops.

Words to strike, and what goes in their place:

| Strike | Write |
|---|---|
| This PR adds / introduces / implements | the change, present tense: `checks the response status` |
| great work, nice, solid, LGTM | nothing — praise is not information |
| great, clean, elegant, robust, seamless | the property that holds: `retries on 5xx` |
| crucial, critical, significant, key | the consequence: `drops the last batch` |
| comprehensive, various, several improvements | the list, or the count |
| refactored for better maintainability | what moved where: `moved retry into fetchWithBackoff` |
| it's worth noting that, I think we could possibly | the claim, once |
| leverage, utilise | use |
| in order to | to |
| ensure, facilitate, delve into, holistic | check, let, read |
| emoji, exclamation marks | nothing |

---

## Mode: body

### 1. Pin the target

The argument names a base ref, a PR, the word `stack`, or nothing.

- **Base ref given** → diff against it.
- **Absent** → `git diff <default-branch>...HEAD` (three-dot, against the merge-base), default branch from `gh repo view --json defaultBranchRef -q .defaultBranchRef.name`.
- **PR exists for the branch** (`gh pr view --json number,title,url`) → step 5 edits it rather than creating one.
- **`stack`** → read [`../split-prs/DEPLOYABLE.md`](../split-prs/DEPLOYABLE.md) and the process in [`../split-prs/SKILL.md`](../split-prs/SKILL.md), and follow them for the survey, the slice proposal, the approval gate, and the `gh stack` rebuild. Keep the grain coarse. Each slice's body then runs steps 2–5.

Also capture `git log <base>..HEAD --oneline`. The diff is the subject of the body; commit messages, branch name and any existing PR description are context.

### 2. Find the template

**The repo's template sets the shape. This skill sets the words.** Take the first that exists:

1. `.github/PULL_REQUEST_TEMPLATE.md` or `.github/pull_request_template.md`
2. `PULL_REQUEST_TEMPLATE.md` or `docs/PULL_REQUEST_TEMPLATE.md` at the root
3. `.github/PULL_REQUEST_TEMPLATE/<name>.md` — more than one, ask which
4. None of the above → [`../prepare-for-review/TEMPLATE.md`](../prepare-for-review/TEMPLATE.md)
5. That file missing too → the default shape in step 3

Then:

- **Keep every heading, in the template's order, spelled as the template spells it.** Do not add headings it does not have, and do not rename its headings to the ones in this skill's example.
- **Keep its checkboxes and its literal boilerplate** — checklists, disclaimers, the AI-assistance line. Leave every box unchecked unless the template says the author ticks it.
- **Drop the guidance comments** — `<!-- ... -->` prompts and placeholder angle-brackets are instructions to the author, not content.
- **Omit a section whose source is empty** — no `N/A`, no placeholder. Unless the template marks it required, in which case say the one true line.
- **Replace its prose instruction with bullets.** A template asking for "2–4 sentences describing the problem" gets 2–4 bullets. That substitution is the whole point of this skill.

### 3. Fill it

With no template anywhere, this is the shape:

```md
## Problem

- Uploads over 5 MB fail silently — the user sees a success toast, the file never lands.
- Closes #412.

## Solution

- `upload.ts` checks the response status before showing the toast.
- Failures surface the gateway message inline, under the file picker.
- Retries 3x on 5xx, then stops and keeps the file selected.

**Alternatives considered**

- Raising the gateway limit to 25 MB — skipped, the timeout hits first.

**Breaking changes:** none.

## Screenshots

| Before | After |
|---|---|
| <img src="<url>" width="400"> | <img src="<url>" width="400"> |

## Tests

**Automated**

- `upload.test.ts` — a 500 response shows the error, not the toast.
- `upload.test.ts` — retries stop after 3 attempts.

**Manual**

- [ ] Throttle to offline, upload a 6 MB file.
- [ ] Expect an inline error, with the file still selected.
```

Diff-first. Fold each source in **only if present**, and never block on a missing one: `.scratch/<feature>/decisions.md` breadcrumbs, `docs/adr/` entries touching paths in the diff, the spec or ticket named in a commit message.

Section rules — apply each to the template's equivalent section, whatever it is called:

- **Whole body at most 250 words.**
- **Problem** — at most 3 bullets, in user-visible terms a product teammate already recognises. `Closes <ref>` as its own last bullet when a ticket exists.
- **Solution** — at most 6 bullets, each naming a symbol or path spelled exactly as the diff spells it. Say what changed and what it now does. A seventh bullet means the PR wants slicing — offer `stack`.
- **Alternatives considered** — one bullet per breadcrumb (`kind: pr-body`) or rejected ADR option, shaped `<option> — skipped, <reason>`. Both sources empty, the block goes.
- **Breaking changes** — one line: `none.` or `<what breaks> + <migration step>`.
- **Screenshots** — frontend diff only. Backend-only, the heading does not appear, unless the template requires it. Capture flow: [`../prepare-for-review/SCREENSHOTS.md`](../prepare-for-review/SCREENSHOTS.md), run only on request.
- **Tests / Automated** — one bullet per case, naming a test file in the diff and the behaviour it pins.
- **Tests / Manual** — reviewer TODO, every box unchecked, one action per line, runnable without the spec. Omit any scenario the automated bullets already cover. A template grouping these as `TC1: <scenario>` keeps that grouping.

### 4. Audit the draft

Check it line by line and rewrite until each passes:

- Headings match the template's, in its order, with nothing added and nothing renamed.
- Every required section from the template is present; every empty optional one is gone.
- Every bullet is one line of at most 20 words; the body is at most 250 words.
- Every Solution bullet names a symbol or path that appears in the diff.
- Every Automated bullet names a test file that appears in the diff.
- Every checkbox is unchecked.
- Zero words from the strike table, zero praise, zero stacked hedges.
- Nothing on the page outside the template's sections — no preamble, no closing summary.

Report only once the draft passes clean.

### 5. Apply

Show the assembled body and the push plan. Wait for explicit approval, then:

- No PR yet → `git push -u origin <branch>` (plain `git push` if upstream is set), then `gh pr create --title "<title>" --body-file <tmp>`.
- PR exists → `gh pr edit <n> --body-file <tmp>`.
- Stack → the PRs already exist from `gh stack submit`; edit each, bottom to top.

Titles take the changelog voice too: one line, no trailing period, subject shape from `docs/agents/commit-style.md` when it exists. Print the PR URL.

---

## Mode: reply

### 1. Pull the threads

```bash
gh pr view <pr> --json number,url,headRefOid,comments,reviews
gh api repos/{owner}/{repo}/pulls/{n}/comments   # inline review comments, with in_reply_to_id
```

Group the inline comments into threads by `in_reply_to_id`, and pin each thread to its `path` and `line`. Skip a thread whose last comment is already yours, and skip one the author marked resolved.

For each thread, read the code it anchors to as it stands **now** — `git log <base>..HEAD` may already contain the fix.

### 2. Settle each thread

Pick one disposition per thread, and say which in the first bullet:

| Disposition | First bullet |
|---|---|
| Fixed | `Fixed in <sha> — <what changed>.` |
| Already handled | `<symbol> already does this — <where>.` |
| Won't do | `Skipped — <reason>.` |
| Disagree | `<the counter-claim>, because <mechanism>.` |
| Question back | `<the question>?` |

Never agree to a change you have not made. A promise is `Will do in a follow-up — <ref>`, and it needs a ticket or an issue behind it.

### 3. Write it up

The shape, exactly:

```md
- Fixed in `a1b2c3d` — `parseAmount` now returns `null`, and the guard rejects it.
- The empty-string case has a test: `amount.test.ts:31`.
```

```md
- Skipped — the 30s timeout is deliberate, the upstream gateway retries twice at 10s.
- Dropping to 10s would cut the second retry.
```

Rules — the voice contract, plus:

- **At most 4 bullets per thread.** One is normal.
- **The first bullet is the disposition.** Everything after it is evidence.
- **Cite, don't assert** — a commit SHA, a `file:line`, a test name. A reply with no anchor is an opinion.
- **No bullet marker inside a GitHub reply body when the reply is a single sentence** — one sentence stands alone; two or more go as bullets.
- **Answer the comment that was written**, not the one that is easier to answer.

### 4. Audit the draft

- Every thread has a reply, and every reply opens with its disposition.
- Every claim of a fix names a SHA or a `file:line` that exists.
- Zero words from the strike table, zero apologies, zero restating the reviewer's comment back at them.
- No reply exceeds 4 bullets of 20 words.

### 5. Post, on approval

Print every reply next to the comment it answers, and wait for explicit approval. Then:

- **Inline thread** → `gh api repos/{owner}/{repo}/pulls/{n}/comments/{comment_id}/replies --method POST -f body=@<tmp>`, where `comment_id` is the **first** comment in the thread. This keeps the reply in the thread.
- **Top-level PR comment** → `gh pr comment <n> --body-file <tmp>`.
- **Do not** post an inline answer as a bottom-of-PR comment — it loses the anchor, which is the failure mode this mode exists to avoid.

Skip a closed, merged, or draft PR. Print the URL of each reply.
