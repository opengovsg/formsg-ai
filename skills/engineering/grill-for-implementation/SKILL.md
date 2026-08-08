---
name: grill-for-implementation
description: Grill a concrete implementation plan into pinned implementation decisions in the spec or tickets.
disable-model-invocation: true
---

Run a `/grilling` session, using the `/domain-modeling` skill.

Identify and decide upfront on all load-bearing engineering and implementation decisions and put them on the frontier, so that the implementation agent must not guess — schema shape, failure modes, ordering, architectural decisions; whichever apply to this feature.

When one settles, pin it: write a **pinned implementation decision** into the spec or tickets. Later agents execute pinned implementation decisions **verbatim**.
