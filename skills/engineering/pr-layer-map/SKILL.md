---
name: pr-layer-map
description: >-
  Generate a Mermaid stack diagram showing which layers of the FormSG codebase a
  pull request touches — frontend pages/UI/API-client, the packages/shared and
  packages/sdk contracts, and backend routes → middlewares → controllers →
  services → models. Output is a fenced mermaid block ready to paste straight
  into a GitHub PR description, where GitHub renders it natively. Use this
  whenever someone asks to visualize, diagram, or map a PR or branch, asks which
  parts of the stack a change touches, asks how a change flows from frontend to
  backend, wants the blast radius or scope of a PR, or is writing up a large PR
  for reviewers. Reach for it even without the word "diagram" — "what does PR
  9893 actually touch?", "is this frontend-only?", and "add a diagram to my PR
  description" all want this.
---

# PR layer map

Produce a Mermaid diagram of which architectural layers a FormSG change touches,
sized and styled to live in a GitHub PR description.

The output is a fenced ```mermaid block and nothing else. GitHub renders Mermaid
natively in PR descriptions and comments, so the diagram travels with the PR
rather than sitting behind a link that reviewers won't open. Keep it that way:
no file tables, no test breakdowns, no companion artifact unless asked. A
reviewer wants one glance that answers "how far does this reach?"

## Generate it

```bash
# A PR, by number or URL
python3 scripts/classify_changes.py --pr 9893 --mermaid

# The current branch against its merge-base (run from the FormSG working dir)
python3 scripts/classify_changes.py --branch --base main --mermaid
```

Add `--no-counts` to drop the `+N −M` annotations and leave bare layer names.

The script emits the complete block — fences included — already styled. Paste
its output verbatim. Don't hand-write Mermaid: the node set, the collapse from
27 classified layers down to the ten-node stack, and the light/dark styling are
all encoded in the script, and regenerating them by hand produces a diagram that
differs PR to PR for no reason.

Drop `--mermaid` to get the underlying JSON instead, when you need the per-file
detail to answer a question the diagram doesn't.

## Reading it back to the user

The diagram shows three states: **filled** layers have source changes,
**outlined** layers changed only in tests, **dashed grey** layers weren't touched
at all. Solid arrows are the request path, dotted arrows are imports, and the
thick arrow is the frontend/backend network boundary.

When you hand it over, say the two or three things the picture implies but
doesn't spell out:

**Where the weight sits.** The largest touched layer is where review attention
belongs.

**Which layers stayed dark, when that means something.** A field PR touching no
routes, middlewares, or controllers adds no endpoint — it rides existing
plumbing. That absence is usually the most reassuring fact about a big diff and
it is invisible in a file list. Mention absences that carry meaning; don't
inventory every unlit box.

**Contract crossings.** `packages/shared` is imported by both sides.
`packages/sdk` is published and consumed by third-party form owners, so a change
there reaches outside the repo entirely — worth flagging even when it's two
lines, because two lines in a published package read as noise in a large diff.

If the PR has a body, skim it (`gh pr view <n> --repo opengovsg/FormSG --json body`).
A diagram that contradicts the author's stated intent, or lights up a layer the
description never mentions, is worth raising.

## Layout notes

The full diagram is top-to-bottom: Frontend, Backend, then Shared contracts as
the foundation both import. A left-to-right flow produces a wide strip that a PR
description column squashes unreadably.

**Contained changes get a compact diagram automatically.** When the touched
layers all sit inside one group and there are at most three of them, the script
drops the full stack and emits a single-row chain of just that group, followed by
a line naming what stayed untouched — "_Contained to the backend — frontend and
shared contracts untouched._" A two-file middleware fix rendered as the whole
stack is ~900px of mostly-dim boxes to make a point one sentence makes better.

Contract-only changes never compact. `packages/shared` and `packages/sdk` are
imported from everywhere, so the wide view showing what sits above them is the
entire story.

Every node is styled with explicit colors rather than inherited ones, because
GitHub renders the same block against a light or a dark canvas and gives the
diagram no way to know which. Touched nodes carry a solid fill with white text;
untouched nodes use `fill:none` so they take whatever background they land on.
If you ever edit the styling, preserve that property — a diagram that only works
in light mode is broken for half the team.

## Keeping the layer rules current

`references/layers.md` documents what each classified layer means, which paths
are ambiguous and how they resolve, and how the fine-grained layers collapse into
the ten diagram nodes. Read it when a file lands somewhere surprising.

FormSG's structure moves. When a rule misfires, fix the ordered `RULES` list in
the script rather than patching the output. Anything matching no rule lands in
`unknown`; a non-empty `unknown` bucket (visible in the JSON output) means the
rules have fallen behind the repo.
