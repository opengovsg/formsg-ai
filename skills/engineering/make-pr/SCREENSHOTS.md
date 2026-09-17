# Frontend Screenshots

Run only if the diff looks frontend. Uses the `agent-browser` CLI (assumed installed; if `agent-browser --version` fails, skip this section and note in the PR body).

## Detection

Heuristic: any file in the diff with extension `.tsx`, `.ts`, `.jsx`, `.js`, `.vue`, `.svelte`, `.css`, `.scss`, `.html` *inside a directory that looks frontend* (`app/`, `src/components/`, `src/pages/`, `web/`, `frontend/`, `client/`, etc.). A backend TypeScript service does not count. If ambiguous, ask: "I see changes to `<files>`. Should I capture screenshots?".

## Pre-flight

Ask: "Start your dev server, log in in the agent-browser window if the app requires it, then paste the base URL." Wait for the URL. Then verify `git status --porcelain` is empty. If dirty, stop and ask the user to commit or stash — do not auto-stash.

## URL list

1. If the PRD has a "User journey" or explicit pages list, seed from it.
2. Else, infer URLs from changed file paths via framework convention (Next.js `app/`/`pages/`, SvelteKit `src/routes/`, Remix `app/routes/`). If the framework is unrecognised and the PRD is silent, ask the user.
3. Present the proposed URL list and wait for explicit confirmation before capturing.

Slug = kebab-case of the route. `/settings/team` → `settings-team`; `/` → `root`.

## Capture

One-liner template (delegate everything else — selectors, clicks, waits — to `agent-browser skills get core`):

```sh
agent-browser open "$BASE_URL/billing"
agent-browser screenshot ".github/screenshots/<feature>/after-billing.png"
```

**Order: after first, then before.**

1. Record current `HEAD` ref.
2. For each URL: `agent-browser open` → `screenshot after-<slug>.png`.
3. `git checkout <fixed-point>` and wait briefly for the dev server to hot-reload.
4. For each URL: `agent-browser open` → `screenshot before-<slug>.png`.
5. `git checkout <original-HEAD>` to restore. If any step after step 3 fails, tell the user explicitly: "You are on `<fixed-point>`; run `git checkout <branch>` to return."
6. `agent-browser close`.

**Degradation paths.** If the dev server doesn't hot-reload across the checkout (production build, lockfile drift, schema/migration mismatch), skip before for that page, fall back to after-only, and note "before unavailable — `<reason>`" in the PR body.

**Journey steps** (only if PRD has a "User journey" section): perform each step with `agent-browser` commands, capture as `journey-<n>-<slug>.png`. See `agent-browser skills get core` for click/wait/selector syntax.

## Persisted manifest

Write the capture commands to `.scratch/<feature>/screenshots.sh` so follow-up PRs can re-run without re-deriving:

```sh
#!/usr/bin/env bash
set -e
: "${BASE_URL:?set BASE_URL}"
agent-browser open "$BASE_URL/billing"
agent-browser screenshot ".github/screenshots/<feature>/after-billing.png"
# ...
agent-browser close
```

If the file already exists, merge new URL lines in rather than overwriting.

## Pushing images

Images go to a long-lived orphan branch named `screenshots`, never merged. Use a worktree so the feature branch's working tree never sees the PNGs.

First time only: `git switch --orphan screenshots && git commit --allow-empty -m "init screenshots" && git push -u origin screenshots && git switch -`.

```sh
git worktree add /tmp/<repo>-screenshots screenshots
# copy PNGs into /tmp/<repo>-screenshots/.github/screenshots/<feature>/
git -C /tmp/<repo>-screenshots add .github/screenshots/<feature>
git -C /tmp/<repo>-screenshots commit -m "chore(screenshots): capture <feature> before/after"
git -C /tmp/<repo>-screenshots push
git worktree remove /tmp/<repo>-screenshots
```

## Embedding

Raw GitHub URLs, branch `screenshots` (not a SHA — embeds update on re-capture):

```
https://raw.githubusercontent.com/<owner>/<repo>/screenshots/.github/screenshots/<feature>/<file>.png
```

## PR body sub-section format

Slot between **Alternatives considered** and **Breaking Changes**:

```md
**Screenshots**

| Page | Before | After |
| --- | --- | --- |
| `/path` | ![before](<raw-url>) | ![after](<raw-url>) |

**User journey: `<journey name>`**  <!-- only if PRD has one -->

1. ![step 1 — <caption>](<raw-url>)
2. ![step 2 — <caption>](<raw-url>)
```

No frontend changes → sub-section omitted entirely.
