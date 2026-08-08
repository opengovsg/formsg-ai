# FormSG AI Skills

A collection of agent skills (slash commands and behaviors) loaded by Claude Code. Skills are organized into buckets and consumed by per-repo configuration emitted by `/setup-formsg-ai-skills`.

## Language

**Ticket tracker**:
The tool that hosts a repo's **Tickets** — GitHub Issues, Linear, a local `.scratch/` markdown convention, or similar. Skills like `to-tickets` and `to-spec` read from and write to it. Per-repo configuration for it lives in `docs/agents/ticket-tracker.md`.
_Avoid_: issue tracker, backlog manager, backlog backend, issue host

**Ticket**:
A single tracked unit of work inside a **Ticket tracker** — a bug, a task, or a vertical slice produced by `to-tickets`. A ticket declares its blocking edges, its pinned implementation decisions, and its test gates. A ticket is a ticket wherever it lives: a GitHub issue, a Linear card, or a markdown file under `.scratch/`.
_Avoid_: issue, story, card (use only when quoting a platform's own API — `gh issue create`, a GitHub child issue)

**Spec**:
The document `to-spec` publishes: the settled problem, the decisions behind it, and the pinned decisions an implementation agent must not deviate from. Engineers own it, and it carries implementation decisions rather than product requirements.
_Avoid_: PRD, design doc

**Triage role**:
A canonical state-machine label applied to a **Ticket** during triage (e.g. `needs-triage`, `ready-for-agent`). Each role maps to a real label string in the **Ticket tracker** via `docs/agents/triage-labels.md`.

**Breadcrumb**:
An author-written decision note dropped during implementation, capturing a small in-impl judgment call (the choice, alternatives considered, optional file:line anchor) that's too narrow for an **ADR**. Lives in `.scratch/<feature>/decisions.md` in the consuming repo. Consumed by `prepare-for-review` to populate PR body and inline review comments without re-deriving rationale from the diff.
_Avoid_: "decision log entry" (overlaps with ADR), "comment" (overlaps with code comment / PR comment)

**Design source**:
The canonical visual spec a frontend slice is verified against — typically a Figma file via the Figma MCP, but may be a user-supplied screenshot or description. Used by the `tdd` skill's visual cycle as the grounding for the **Visual gate**. Optional: a slice may have no design source, in which case the visual gate degrades to self-consistency review.
_Avoid_: "mock", "design", "spec" (a **Spec** is the `to-spec` document)

**Visual gate**:
The agent-browser-vs-**Design source** comparison that closes a visual RED→GREEN cycle in the `tdd` skill. Uncommitted (not a regression test); pass bar is "no deviation a designer would flag in review." Distinct from committed visual regression (Chromatic snapshots of stories in CI).
_Avoid_: "visual test" (overlaps with Chromatic/story-based regression)

## Relationships

- A **Ticket tracker** holds many **Tickets**
- A **Ticket** carries one **Triage role** at a time
- A **Spec** produces many **Tickets**; a ticket names the spec it came from

## Flagged ambiguities

- "backlog" was previously used to mean both the *tool* hosting tickets and the *body of work* inside it — resolved: the tool is the **Ticket tracker**; "backlog" is no longer used as a domain term.
- "backlog backend" / "backlog manager" — resolved: collapsed into **Ticket tracker**.
- "issue" carried three senses: the unit of work, the tool that hosts it, and a defect a reviewer finds. Resolved: the unit of work is the **Ticket** and the tool is the **Ticket tracker**, so "issue" now means only a defect (in the `review` skill) or a platform's own word for its records (`gh issue create`, a GitHub child issue).
- "pinned contract" (`grill-for-implementation`) and "pinned implementation decision" (`to-spec`, `to-tickets`) name the same thing — a decision a later agent executes verbatim. Unresolved: the skills still use both.
