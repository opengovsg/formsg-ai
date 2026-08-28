# Query patterns for the three sweeps

How to turn one problem into three genuinely different searches.

## Contents
- [What the Mobbin API rewards](#what-the-mobbin-api-rewards)
- [Sweep 1: in-industry](#sweep-1-in-industry)
- [Sweep 2: out-of-industry](#sweep-2-out-of-industry)
- [Sweep 3: metaphor](#sweep-3-metaphor)
- [Worked examples](#worked-examples)
- [Finding a metaphor when none comes to mind](#finding-a-metaphor-when-none-comes-to-mind)

## What the Mobbin API rewards

The search is natural language, not keywords. It rewards a specific description of one thing and
punishes everything else.

- **Describe one screen or one journey**, in plain language, including the elements you'd expect to
  see. Detail helps.
- **Name an app to scope to it.** "Duolingo onboarding" works as a filter.
- **Don't combine two things.** "Login and signup" returns worse results than two separate searches.
- **Don't use negations.** "Checkout without a promo field" won't do what you want.
- **Don't use style words.** "Modern", "clean", "beautiful" carry no signal.
- **Don't write keyword lists.** "checkout payment card apple pay" reads worse than a sentence.
- **Never put the platform in the query** — it's a separate parameter.
- **Leave `mode` alone on `search_screens`.** It defaults to `"deep"`, Mobbin's pipeline that reads
  intent and scores candidates for relevance. Passing `"standard"` trades that away for latency,
  and it shows: a smart-home query on standard came back with GitHub and Substack, and a medication
  query returned an online course app. Standard is only safe on sweep 1, where you want the obvious
  convention anyway. Sweeps 2 and 3 depend on reaching a specific industry or metaphor, which is
  exactly what deep is for. (`search_flows` and `search_sections` have no mode parameter.)
- **Aim for 10+ screens per sweep.** A single-query sweep uses `limit: 10`. A sweep with three
  probes uses `limit: 4` on each, which gives twelve while keeping every probe focused on its own
  industry or metaphor.

## Sweep 1: in-industry

**Asking:** who solves this for people like ours?

Keep every domain word. Add the audience and the setting. Name two or three comparable products if
you know them.

This sweep is supposed to return the obvious answer. That's its job — it tells you the convention
you'd be breaking. Don't judge it for being predictable, and don't retry it just because it found
what everyone else does.

## Sweep 2: out-of-industry

**Asking:** who solves this same underlying job in a completely different industry?

**Name the industries. Search each one separately.**

The obvious move is to strip the domain words and let the results come from wherever. It doesn't
work. Search returns what's most semantically similar, so a vaguer version of a SaaS query still
returns SaaS — you get the same industry described more loosely. It looks like the sweep worked,
which is what makes it worth warning about.

Instead: pick two or three industries genuinely far from the original, and search the job *inside*
each one. Healthcare, travel, logistics, games, smart home, automotive, education. Each carries
different pressures — safety, cost, urgency, boredom, regulation — and those pressures are what
produce different answers.

"Notification preferences" searched as healthcare returns reminders anchored to morning, afternoon
and evening. Searched as travel it returns tiers of coverage you buy rather than switches you set.
Neither shows up if you just describe alerts vaguely.

Stay on the same platform throughout, so industry is the only variable you changed.

**Optional extra: flip the platform.** Not what sweep 2 means, but a useful second angle when the
job clearly transfers, because the same task under a thumb on a 390px screen has different pressures
than one with a mouse and room to spare.

Add it when you want another cut and the job exists in both places. Skip it when the job is
platform-bound — a swipe-to-dismiss or a hover-reveal has no counterpart worth studying on the other
side. And note that flipping changes two variables at once, so be clear about which result came from
which move.

## Sweep 3: metaphor

**Asking:** what else is this a kind of?

The other two sweeps look for the same job elsewhere. This one changes what you think the job is.

The move: answer "what else is this a kind of?" first, then **search the metaphor's own domain
instead of the original problem.** That's the part people get wrong — they keep searching the
original problem with a metaphor-flavoured adjective bolted on, which returns the same results.

- A form is a kind of interview → search conversational question flows, not forms
- A settings page is a kind of control panel, or a recipe → search mixing desks, or step-by-step
  instructions
- A dashboard is a kind of newspaper → search article layouts and front pages
- Choosing a plan is a kind of menu → search restaurant ordering

**Search each metaphor separately.** Two or three searches, a couple of results from each.

This is the step people get wrong, and the mistake is easy to miss because the sweep still looks
like it worked. Pick one metaphor, pull six results, and you have six mixing desks: one idea
explored six times. That's the numpad failure again, hiding inside the sweep that exists to prevent
it. Two thin searches across different metaphors beat one deep search into a single one.

Pick metaphors that are unlike *each other*, not just unlike the original problem. Notification
settings are a mixing desk (levels), a mail rule (conditions and destinations), and a thermostat
schedule (intensity by time of day). Those three disagree with each other, so they produce three
different directions. Mixing desk, equaliser and DJ deck are one metaphor wearing three hats.

## Worked examples

**Problem:** someone booking an appointment needs to pick a time slot. iOS. Component altitude, so
`search_screens`.

| Sweep | Query |
|---|---|
| 1 | "appointment booking screen showing available time slots for a selected day" |
| 2 | Healthcare: "booking a clinic appointment slot" / Restaurants: "choosing a table reservation time" — separate searches, still iOS |
| 3 | "seat selection map for choosing a seat before checkout" (a time slot is a kind of seat) |

Sweep 3 reframes time as inventory laid out in space. It returns seat maps and floor plans, which
suggest a grid or map of the day rather than a list — a direction the first two sweeps cannot reach.

---

**Problem:** viewing the detail of one row from a 200-row table. Web. Flow structure, so
`search_flows`.

| Sweep | Query |
|---|---|
| 1 | "opening a record from a data table to see its full details" |
| 2 | Music: "opening one track from a library listing" / Email: "opening one message from an inbox list" — separate searches |
| 3 | "flipping through a card index or file drawer to read one card" (list-to-detail is a kind of card index) |

Stripping "data table" and "record" is what does the work — the bare job of browsing and opening one
item shows up in mail clients, music libraries and photo apps, none of which would surface under the
original query. If you also flip to iOS, mobile's lack of room for a side panel forces full-page and
bottom-sheet answers, which is a useful second cut.

---

**Problem:** a pricing page for a SaaS product. Web marketing, so `search_sections`. No platform
parameter.

| Sweep | Query |
|---|---|
| 1 | "pricing page with a three-tier plan comparison table" |
| 2 | Insurance: "comparing cover levels side by side" / Gyms: "membership tier comparison" — separate searches |
| 3 | "restaurant menu with dishes grouped by course" (a pricing page is a kind of menu) |

## Finding a metaphor when none comes to mind

Sweep 3 stalls when you can't think of one. Prompts that tend to unstick it:

- What is the user **actually doing**, stripped of the interface? Choosing, comparing, committing,
  waiting, remembering, deciding.
- Where does that same act happen **outside software entirely**? A shop, a kitchen, a form on paper,
  a conversation, a queue.
- What did this **look like before computers**?
- If this were a **physical object**, what would it be?

Pick the answer that feels furthest from the original problem. The uncomfortable one is usually the
one that produces range.
