# Matt Pocock Skills

A collection of agent skills (slash commands and behaviors) loaded by Claude Code. Skills are organized into buckets and consumed by per-repo configuration emitted by `/setup-matt-pocock-skills`.

## Language

**Issue tracker**:
The tool that hosts a repo's issues — GitHub Issues, Linear, a local `.scratch/` markdown convention, or similar. Skills like `to-issues`, `to-prd`, `triage`, and `qa` read from and write to it.
_Avoid_: backlog manager, backlog backend, issue host

**Issue**:
A single tracked unit of work inside an **Issue tracker** — a bug, task, PRD, or slice produced by `to-issues`.
_Avoid_: ticket (use only when quoting external systems that call them tickets)

**Triage role**:
A canonical state-machine label applied to an **Issue** during triage (e.g. `needs-triage`, `ready-for-afk`). Each role maps to a real label string in the **Issue tracker** via `docs/agents/triage-labels.md`.

**Breadcrumb**:
An author-written decision note dropped during implementation, capturing a small in-impl judgment call (the choice, alternatives considered, optional file:line anchor) that's too narrow for an **ADR**. Lives in `.scratch/<feature>/decisions.md` in the consuming repo. Consumed by `prepare-for-review` to populate PR body and inline review comments without re-deriving rationale from the diff.
_Avoid_: "decision log entry" (overlaps with ADR), "comment" (overlaps with code comment / PR comment)

**Design source**:
The canonical visual spec a frontend slice is verified against — typically a Figma file via the Figma MCP, but may be a user-supplied screenshot or description. Used by the `tdd` skill's visual cycle as the grounding for the **Visual gate**. Optional: a slice may have no design source, in which case the visual gate degrades to self-consistency review.
_Avoid_: "mock", "design", "spec" (overloaded)

**Visual gate**:
The agent-browser-vs-**Design source** comparison that closes a visual RED→GREEN cycle in the `tdd` skill. Uncommitted (not a regression test); pass bar is "no deviation a designer would flag in review." Distinct from committed visual regression (Chromatic snapshots of stories in CI).
_Avoid_: "visual test" (overlaps with Chromatic/story-based regression)

## Relationships

- An **Issue tracker** holds many **Issues**
- An **Issue** carries one **Triage role** at a time

## Flagged ambiguities

- "backlog" was previously used to mean both the *tool* hosting issues and the *body of work* inside it — resolved: the tool is the **Issue tracker**; "backlog" is no longer used as a domain term.
- "backlog backend" / "backlog manager" — resolved: collapsed into **Issue tracker**.
