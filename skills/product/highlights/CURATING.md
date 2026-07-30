# Curating

Turning a few hundred raw findings into the handful that belong on a public
page. Do this with every source visible at once — the ranking signal only
exists across sources.

## Rank by corroboration

**An item appearing in more than one source is almost always a highlight.**

A real example: a v4 encryption rollout was filed as a routine refactor by the
GitHub pass, because that is what the PR titles looked like. Slack showed it
tracked as a milestone with a success metric; the Notion log tracked it weekly
all quarter. Three appearances meant it was the biggest item of the quarter.
The ~190 dependency bumps appeared once each, in one source.

Ranking, strongest first:

1. In all sources, with a number attached
2. In Slack or the planning doc with an outcome — someone reported it worked
3. In the planning doc as an intent **and** in GitHub as merged code
4. GitHub only, user-visible
5. GitHub only, internal — almost never publish

## What each source is actually good for

| Source | Gives you | Blind to |
| --- | --- | --- |
| GitHub | What was built, exact dates | Whether anyone used it, anything without code |
| Slack | Outcomes, adoption, real numbers | Anything not worth announcing |
| Planning doc | Intent, and what was dropped | What actually shipped |

**GitHub alone produces a feature list with no evidence anything worked.**
Adoption numbers, training sessions, and school or agency onboarding leave no
code trace at all, yet they are often what moved the metrics on the report
card.

The planning doc is the only place that shows **descoped** work. Worth a look:
something dropped for a good reason is occasionally a better story than
something shipped.

## What to cut

- Dependency bumps, CI, refactors, test changes — usually 70% of merged PRs
- Bug fixes, unless the bug was widely felt or the fix is itself a feature
- Internal team matters: hiring, leave, tooling experiments, token costs
- Security vulnerability details. Note that hardening happened; do not
  enumerate what was exploitable
- Anything you cannot trace to a source

## Writing it

- **Plain language.** Public officers read this, not the team. Internal names
  get a plain-English gloss: an internal schema name is fine in parentheses if
  the line explains what changed for users.
- **Do not claim what has not landed.** Something merged behind a feature flag
  and announced next quarter belongs in next quarter's entry. Say "rolled out
  to X" only if it was.
- **Keep numbers exactly as reported.** `27.7k submissions` not `~28k`.
  Rounding a sourced figure makes it untraceable.
- Group under the same top-level headings the last entry used, even if the
  fit is imperfect. Consistency across quarters beats a tidier taxonomy.

## Before handing over

State plainly:

- which sources were unreachable, and what may be missing as a result
- which items you cut that were arguable, so the PM can overrule you
- every placeholder, and where the number would come from

Never present a draft as complete when a source failed. Silence about a gap
reads as "there was nothing there".
