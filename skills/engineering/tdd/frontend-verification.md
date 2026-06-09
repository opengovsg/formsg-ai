# Frontend Verification

Extends the TDD loop for slices that render UI. Same vertical-slicing rule as [SKILL.md](SKILL.md) — one slice runs one unified loop; each cycle picks the assertion mode the next behavior demands.

## One slice, walked through

Slice: "user can submit the contact form."

```
Cycle 1 — visual    RED: add ContactForm.stories.tsx default story; story fails to render (no component yet)
                    GREEN: implement ContactForm renders inputs + submit button using design tokens
                    GATE:  agent-browser opens story URL, compares to Figma → matches → green

Cycle 2 — interaction
                    RED: RTL test "submitting valid form calls onSubmit with values" fails
                    GREEN: wire form state + onSubmit → test passes

Cycle 3 — visual    RED: add ContactForm.stories.tsx "error" variant; visual gate against Figma error state fails
                    GREEN: render error styling with design tokens → gate passes

Cycle 4 — interaction
                    RED: RTL test "empty submit shows validation error" fails
                    GREEN: add validation → test passes

Refactor            Extract repeated padding literal to a spacing token; collapse two near-duplicate story variants.
```

Stories accrue as Chromatic regression fixtures along the way. The visual gate is uncommitted — it runs only inside the cycle.

## When this file applies

During planning, ask:

1. Does this slice render UI?
2. If yes — is it a **component**, a **page/composition**, or **both**?
3. Is there a **design source** (Figma via MCP, or a user-supplied screenshot)?
4. Is Storybook configured in this project?

Routing:

| Slice shape                     | Visual cycle target            |
|---------------------------------|--------------------------------|
| No UI                           | Skip this file; use SKILL.md.  |
| Component, Storybook present    | Story-as-RED.                  |
| Page or composition             | Dev-route-as-RED.              |
| Component **and** page          | Story-as-RED for component; dev-route gate for page. |
| Component, no Storybook         | Dev-route-as-RED (degraded — no isolated state coverage, no Chromatic regression). |

If no design source is available, the **visual gate** degrades to self-consistency (renders, no obvious layout breaks) and the agent flags the gap to the user instead of silently passing.

## Two RED modes within one slice

A frontend slice alternates between cycle types as needed:

- **Visual cycle** — RED: a new story (or a new dev-server route render) that doesn't yet match the design source. GREEN: component renders + **visual gate** passes.
- **Interaction cycle** — RED: a behavior test (RTL/Playwright) for a capability. GREEN: test passes.

Rule of thumb: a state that's *observable user behavior* gets an interaction cycle ("user sees error on invalid submit"). A state that's purely visual gets a visual cycle ("loading skeleton matches Figma"). Don't write all visual cycles first then all interaction cycles — that's horizontal slicing.

**First tracer bullet for a visual slice is always a visual cycle.** Minimum proof the path works: the component exists, is wired into its parent/route, renders, and uses design tokens from the design source. Interaction tests come immediately after, against something that actually exists on screen.

## The visual gate

The visual gate closes a visual RED→GREEN cycle. It is **not** committed and **not** a regression test — Chromatic snapshots of stories handle regression in CI.

Mechanics:

1. Bring up the render target:
   - Story target: ensure Storybook is running locally; the story URL is the target.
   - Dev-route target: ensure the dev server is running; the route URL is the target.
2. `agent-browser open <url>` → `agent-browser screenshot <path>` for the impl render. See [SCREENSHOTS.md](../prepare-for-review/SCREENSHOTS.md) for the CLI patterns.
3. Pull the corresponding screenshot from the design source (Figma MCP `get_screenshot`, or the user-supplied image).
4. Compare side-by-side. Pass bar: **no deviation a designer would flag in review** — layout, spacing, color, typography. Anti-aliasing differences and platform font rendering are not deviations.
5. If deviation: iterate impl (often: swap a hardcoded value for a design token), re-gate. If no design source: declare a self-consistency pass and note the gap.

The agent declares green autonomously. Users can override after the fact; this is an autonomous loop, not a confirm-each-step loop.

## Design tokens are mandatory when a design source is present

If Figma MCP is connected, pull `get_variable_defs` during planning and use those tokens in the impl. Hardcoded `#3B82F6` is the frontend equivalent of ignoring the domain glossary. Without a connected design source, project conventions take over.

## Stories

When the visual cycle targets a story, the story file is the committed RED artifact. The skill stays silent on story file location, naming, and CSF version — defer to project conventions, then to Storybook defaults. A state that deserves an interaction cycle should also surface as a story variant where natural, so Chromatic picks it up for regression.

## Refactor

Same rules as [refactoring.md](refactoring.md), plus a frontend-specific lens:

- Extract repeated literal style values into design tokens.
- Extract recurring layout/visual patterns into shared components.
- Collapse story variants that duplicate the same visual state.

Never refactor while RED — including a failing visual gate.

## Degraded modes — summary

| Missing                  | Effect                                                              |
|--------------------------|---------------------------------------------------------------------|
| Figma MCP / design source| Visual gate becomes self-consistency only; flag gap to user.        |
| Storybook                | Component slices use dev-route-as-RED; no Chromatic regression.     |
| `agent-browser`          | Visual gate skipped entirely; note in breadcrumbs.                  |

## Checklist per visual cycle

```
[ ] RED artifact (story or dev-route attempt) does not yet match design source
[ ] Impl uses design tokens from the design source where present
[ ] Visual gate run via agent-browser against design source
[ ] No deviation a designer would flag in review
[ ] Story variant captured for any new visual state (when Storybook present)
[ ] Breadcrumb dropped for non-obvious in-impl visual choices
```
