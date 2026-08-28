---
name: mobbin-reference-sweep
description: "Collect design references on Mobbin using a three-sweep method that produces genuinely different directions instead of three versions of the same idea. Use this whenever someone wants design references, UI examples, prior art, or inspiration — including 'find references for X', 'how do other apps handle X', 'search Mobbin for X', 'show me examples of X', 'what are the options for this UI', or when they're exploring approaches to a design problem before committing to one. Use it even when Mobbin is never mentioned by name, and even when the request sounds like a simple lookup, because the value is in searching three different ways rather than accepting the first obvious answer."
---

# Mobbin reference sweep

Most people search for references once, find the conventional answer, and stop. They end up with
three screenshots of the same idea and call it exploration. This skill searches the same problem
three different ways so what comes back is a set of real alternatives.

## The prerequisite: know what you're looking for

A search without an aimed problem returns things that look nice rather than things that fit.

Before searching, you need a one-line problem: **who** is doing **what**, under **what constraints**.

Usually the request already contains this. Infer it, say it back in one sentence, and continue —
don't interrogate someone who already knows what they want. Ask a single question only when the
request is too vague to write a decent query from ("find me some references" with no subject).

## Step 1: Altitude picks the tool

The grain of the problem decides which unit you search. Get this wrong and the results look fine
but answer a different question — a flow problem answered with single screens is quietly useless
rather than obviously wrong.

| Altitude | The problem is about | Tool |
|---|---|---|
| Component | One control or element. Entering a time, picking a date | `search_screens` |
| Screen system | One screen's worth of machinery. Filtering a long list | `search_screens`, queried wider |
| Flow structure | A sequence. Getting from a list of 200 rows to one row's detail | `search_flows` |
| Web marketing | A page block on a marketing site. Pricing, About, Footer | `search_sections` |

Say which one you picked and why, in one clause: *"this is a flow question, so I'm searching full
flows rather than screens."* That sentence is the most portable idea here, and saying it every time
is how someone picks up the habit.

**Platform** is required for `search_screens` and `search_flows`, and there is no "both". Infer it
and state it. `search_sections` has no platform parameter.

## Step 2: Run three sweeps

Mobbin's MCP has **no industry filter** — only a natural-language query. So the sweeps are three
rewrites of the same search, not three filter settings. This is the part someone can't reconstruct
from webapp habits, and it's what makes the difference between one search and real range.

| Sweep | The question | How the query changes |
|---|---|---|
| 1. In-industry | Who solves this for people like ours? | Keep the domain words. Name comparable apps |
| 2. Out-of-industry | Who solves this same job in a completely different industry? | Name 2-3 far-away industries, search each separately. Same platform |
| 3. Metaphor | What else is this a kind of? | Query the metaphor's own domain, not the original problem |

Read [`QUERY-PATTERNS.md`](QUERY-PATTERNS.md) before writing the queries. It has worked rewrites and the
query rules the Mobbin API actually rewards.

**Run sweep 2 as two or three separate searches, one per industry.** Naming the industry is the
whole move. Stripping the domain words and hoping for variety does not work: the search returns
whatever is most semantically similar, so a vaguer version of a SaaS query still returns SaaS. You
get the same industry described more loosely, which looks like a successful sweep and isn't.

Pick industries genuinely far from the original — healthcare, travel, logistics, games, smart home,
automotive — and search the job inside each one. Different sectors carry different pressures:
safety, cost, urgency, boredom, regulation. Those pressures are what produce different answers.

Stay on the same platform throughout, so industry is the only variable you changed.

**Flipping platform is an optional extra**, not what the sweep means. It's worth adding when the job
clearly transfers and you want a second angle, because the same task under a thumb on a small screen
has different pressures than one with a mouse and room to spare. Skip it when the job is
platform-bound: a swipe-to-dismiss or a hover-reveal has no counterpart worth studying on the other
side. If you do flip, say so, and be aware you've now changed two things at once.

**Sweep 3 is the one that generates range, and it's the one people skip**, because it takes a moment
of thought before you can type anything. It's also the only sweep no filter could ever do for you.
If a form is a kind of interview, search interviews. If a dashboard is a kind of newspaper, search
newspapers.

**Run sweep 3 as two or three separate searches, one per metaphor.** This is the easiest thing to
get wrong. Picking your best metaphor and pulling six results from it gives you six versions of that
one idea — the same failure the whole method exists to catch, just hiding inside the sweep that was
supposed to prevent it. Generate two or three metaphors that are unlike each other, search each one
separately, and take a couple of results from each.

Narrate one line per sweep as you run it.

**Aim for at least 10 screens per sweep.** Fewer than that and a sweep can't show you a pattern —
you can't tell whether three results are the convention or a coincidence. For sweeps that run
several probes, split the target across them: three industries at four results each gives you
twelve, and each probe stays focused.

That means roughly 30+ screens across the three sweeps, which is a real amount of context. Spend it
on breadth across probes rather than depth within one — four results from each of three industries
beats twelve from one.

**Retry rule:** if a sweep comes back empty, or returns only things already found by an earlier
sweep, retry it once using `exclude_screen_ids` to push away from what you have. One retry. If it's
still narrow, say so plainly — "this problem has a dominant convention" is useful information, not a
failure to hide.

## Step 3: Apply the breadth test

Pool everything and group by underlying concept, not by which sweep found it.

> If you changed your mind about the winner, would any of the others still be on the table?

If the answer is no, they're variations of one idea. Aim to name **three structurally different
directions**, each with a one-line "what if" framing. Be honest when the results only support two —
padding to three with a variation is precisely the failure this method exists to prevent.

## Step 4: Deliver

**In chat:** results grouped by sweep in order, since that shows the method working, then a short
"distinct directions" summary that regroups across sweeps. Cite every screen as a markdown link to
its `mobbin_url` so people can open it.

**As an artifact:** always. This is the thing someone pastes into a board or shares with a teammate
who wasn't in the conversation.

```bash
python3 scripts/build_artifact.py sweeps.json out.html
```

Write `sweeps.json` in the shape the script documents (problem, then each sweep with its query and
its screens), then publish `out.html` with the Artifact tool. The script downloads each `image_url`
and embeds it as a data URI, which matters for two reasons: artifacts block remote images, and
Mobbin's image links are short-lived, so embedding is what keeps the artifact readable next month.

The script needs `python3` and `curl`, both of which ship with macOS. It has no pip dependencies
on purpose, so it runs straight from a fresh checkout.

Write the artifact's prose like a person wrote it. Short sentences, no throat-clearing, no "this
comprehensive analysis reveals". If you have the `humanizer` skill available, run the copy through
it. The artifact gets shared, so it should read like a colleague's notes rather than generated
output.

## When Mobbin isn't available

The MCP won't be there for everyone — it needs a paid plan, and shared accounts hit device caps.

Say plainly that the Mobbin tools aren't available, then ask whether they'd like to run the same
three sweeps as web searches instead. Don't silently substitute. If they say yes, run the identical
method, produce the same artifact, and label the source clearly so nobody mistakes a blog screenshot
for a real product flow.

The method is worth more than the tool. It transfers to any source.
