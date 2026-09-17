# Deployable slices & grain

A **deployable slice** is one PR that can merge to trunk and ship to production on its own — without needing a later slice for correctness, green CI, or a safe prod state.

## Deployable (definition)

After merging this slice (and only the slices below it in the **stack**):

1. Trunk builds; tests for this slice's scope pass.
2. Production behaviour stays healthy — dormant code, flag-gated paths, additive APIs, or an intentional breaking change called out in the plan.
3. No higher slice is required for *this* slice to be correct.
4. Higher slices rebase onto the new trunk cleanly (`gh stack sync`).

Prefer shapes that keep prod quiet after each merge: additive modules, feature flags, expand-then-contract migrations, pure refactors. When a wire-up would leave a bad intermediate, fold the final shape into the slice that introduces the behaviour.

## Grain

**Grain** is how coarse the cut is. Prefer the coarsest grain that still earns the split.

Split when at least one holds:

- **Review** — a reviewer can hold one story in their head; adjacent concerns would force them to context-switch mid-diff.
- **Risk** — shipping the whole pile at once widens blast radius; a smaller deployable slice shrinks exposure.

Keep together when:

- The pieces share one blast radius (schema + the only code that reads it; flag + the only path behind it).
- Separating them creates a non-deployable intermediate.
- The cut would be cosmetic (file-path boundaries with no independent deploy or review story).

One deployable slice is a valid outcome. Say so and hand off to `prepare-for-review`.

## Ordering the stack

Bottom (closest to trunk) → top:

1. Pure refactors / renames that clear the path
2. Expand steps (new columns, dual-write, new dormant modules)
3. Behaviour behind flags or unused entry points
4. Wire-up / flag-on / contract (delete the old path)

Foundational dependency below; consumer above. Independent concerns can still sit in one stack for review order — each remains deployable onto trunk after the layers below it.
