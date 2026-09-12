#!/usr/bin/env python3
"""Build a self-contained HTML artifact from a reference sweep.

Usage:
    python3 build_artifact.py sweeps.json out.html

Input JSON shape:

{
  "problem": "Someone booking an appointment needs to pick a time slot.",
  "altitude": "Component",
  "tool": "search_screens",
  "platform": "ios",
  "source": "Mobbin",
  "sweeps": [
    {
      "name": "In-industry",
      "question": "Who solves this for people like ours?",
      "query": "appointment booking screen showing available time slots",
      "note": "optional line, e.g. what the domain strip changed",
      "screens": [
        {"image_url": "https://...", "mobbin_url": "https://...", "app_name": "Instacart"}
      ]
    },
    {
      "name": "Metaphor",
      "question": "What else is this a kind of?",
      "probes": [
        {"label": "A time slot is a kind of seat",
         "query": "seat selection map before checkout",
         "screens": [{"image_url": "https://...", "mobbin_url": "https://...", "app_name": "Hamilton"}]}
      ]
    }
  ],
  "directions": [
    {"title": "What if the day were a map instead of a list?",
     "body": "Seat-selection patterns lay inventory out in space...",
     "refs": ["Instacart", "OpenTable"]}
  ],
  "verdict": "Optional honest note, e.g. only two distinct directions here."
}

Use "probes" when one sweep runs several searches. Sweep 3 almost always should: one search per
metaphor, a couple of results each. A single metaphor with six results is that one idea six times,
not range. Sweeps 1 and 2 normally use the simpler "query" + "screens" form.

Images are downloaded and embedded as data URIs. Artifacts block remote images, and Mobbin's
image links are short-lived, so embedding is what keeps the page readable later.
"""

import base64
import html
import json
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

TIMEOUT = 20
MAX_BYTES = 4_000_000  # skip anything absurd; keeps the page under the artifact size cap

# Sniff the format from magic bytes rather than trusting the URL or Content-Type.
# Mobbin serves short links with no file extension, and these are the only formats it returns.
MAGIC = [
    (b"RIFF", "image/webp"),      # bytes 8-12 are "WEBP", but RIFF is enough here
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", "image/png"),
]


def sniff(raw):
    """Return the image type, or None if these bytes aren't an image we recognise.

    Strict on purpose. A dead Mobbin link returns HTTP 400 with an 11-byte "Bad Request"
    body; without this check that text gets base64'd and embedded as a broken image,
    which looks like a rendering bug rather than a missing reference.
    """
    for prefix, ctype in MAGIC:
        if raw.startswith(prefix):
            return ctype
    return None


def fetch_data_uri(url):
    """Download an image and return a data URI, or None if it can't be fetched.

    Uses curl rather than urllib on purpose. Python on macOS frequently ships without
    usable root certificates, so urllib raises CERTIFICATE_VERIFY_FAILED on perfectly
    valid URLs. curl is present on every machine this will run on and needs no pip
    install, which matters for a skill people install by copying a folder.
    """
    if not url:
        return None
    try:
        # -f makes curl return nothing on a 4xx/5xx instead of handing back the error body.
        raw = subprocess.run(
            ["curl", "-sfL", "--max-time", str(TIMEOUT),
             "--max-filesize", str(MAX_BYTES), url],
            capture_output=True, timeout=TIMEOUT + 10,
        ).stdout
    except Exception:
        return None

    if not raw or len(raw) > MAX_BYTES:
        return None

    ctype = sniff(raw)
    if ctype is None:
        return None

    return f"data:{ctype};base64," + base64.b64encode(raw).decode("ascii")


def e(text):
    return html.escape(str(text or ""))


def render_screen(screen):
    label = e(screen.get("app_name") or "Untitled")
    link = screen.get("mobbin_url")
    uri = screen.get("_data_uri")

    if uri:
        media = f'<img src="{uri}" alt="{label}" loading="lazy">'
    else:
        media = '<div class="missing">Image unavailable</div>'

    caption = f'<a href="{e(link)}" target="_blank" rel="noopener">{label}</a>' if link else label
    return f'<figure class="shot">{media}<figcaption>{caption}</figcaption></figure>'


def render_probe(probe):
    """One search within a sweep: its query, an optional label, and its results.

    Sweep 3 normally has several of these — one per metaphor. Running a single metaphor
    and taking N results just returns that one idea N times, which is the exact failure
    the method exists to catch.
    """
    shots = "".join(render_screen(s) for s in probe.get("screens", []))
    if not shots:
        shots = '<p class="empty">Nothing came back for this one.</p>'
    label = f'<p class="probe-label">{e(probe["label"])}</p>' if probe.get("label") else ""
    note = f'<p class="note">{e(probe["note"])}</p>' if probe.get("note") else ""
    return f"""
      <div class="probe">
        {label}
        <p class="query"><span>Searched</span> {e(probe.get('query'))}</p>
        {note}
        <div class="grid">{shots}</div>
      </div>"""


def render_sweep(index, sweep):
    # A sweep is either one search (query + screens) or several (probes).
    probes = sweep.get("probes")
    if not probes:
        probes = [{"query": sweep.get("query"), "note": sweep.get("note"),
                   "screens": sweep.get("screens", [])}]

    body = "".join(render_probe(p) for p in probes)
    return f"""
    <section class="sweep">
      <div class="sweep-head">
        <span class="num">{index}</span>
        <div>
          <h2>{e(sweep.get('name'))}</h2>
          <p class="question">{e(sweep.get('question'))}</p>
        </div>
      </div>
      {body}
    </section>"""


def render_directions(directions, verdict):
    if not directions:
        return ""
    items = ""
    for d in directions:
        refs = d.get("refs") or []
        ref_line = f'<p class="refs">{e(", ".join(refs))}</p>' if refs else ""
        items += f"""
        <li>
          <h3>{e(d.get('title'))}</h3>
          <p>{e(d.get('body'))}</p>
          {ref_line}
        </li>"""
    v = f'<p class="verdict">{e(verdict)}</p>' if verdict else ""
    return f"""
    <section class="directions">
      <h2>Distinct directions</h2>
      <ol>{items}</ol>
      {v}
    </section>"""


CSS = """
:root {
  --bg: #fdfdfc; --fg: #16181d; --muted: #5d6470; --line: #e2e5ea;
  --card: #f5f6f8; --accent: #2c4bd0;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #14161a; --fg: #eceef1; --muted: #9aa3ae; --line: #2b3038;
    --card: #1b1e24; --accent: #8fb0ff;
  }
}
:root[data-theme="dark"] {
  --bg: #14161a; --fg: #eceef1; --muted: #9aa3ae; --line: #2b3038;
  --card: #1b1e24; --accent: #8fb0ff;
}
* { box-sizing: border-box; }
body {
  background: var(--bg); color: var(--fg); margin: 0;
  font: 16px/1.55 "Instrument Sans", ui-sans-serif, -apple-system, "Segoe UI",
        Roboto, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
}
h1, h2, h3 { font-weight: 600; text-wrap: balance; }
.wrap { max-width: 1100px; margin: 0 auto; padding: 56px 24px 96px; }
header { border-bottom: 1px solid var(--line); padding-bottom: 28px; margin-bottom: 40px; }
h1 { font-size: 1.9rem; line-height: 1.2; margin: 0 0 12px; letter-spacing: -0.02em; }
.problem { font-size: 1.05rem; margin: 0 0 18px; max-width: 62ch; }
.meta { display: flex; flex-wrap: wrap; gap: 8px; margin: 0; padding: 0; list-style: none; }
.meta li {
  font-size: 0.78rem; color: var(--muted); border: 1px solid var(--line);
  border-radius: 999px; padding: 3px 11px; white-space: nowrap;
}
.sweep { margin-bottom: 56px; }
.sweep-head { display: flex; gap: 14px; align-items: flex-start; margin-bottom: 10px; }
.num {
  flex: none; width: 30px; height: 30px; border-radius: 50%;
  background: var(--fg); color: var(--bg);
  display: grid; place-items: center; font-size: 0.85rem; font-weight: 600;
}
.sweep h2 { font-size: 1.2rem; margin: 2px 0 2px; letter-spacing: -0.01em; }
.question { color: var(--muted); margin: 0; font-size: 0.95rem; }
.query {
  font: 0.85rem/1.5 ui-monospace, SFMono-Regular, Menlo, monospace;
  background: var(--card); border: 1px solid var(--line); border-radius: 8px;
  padding: 9px 13px; margin: 14px 0 0; overflow-x: auto;
}
.query span { color: var(--muted); margin-right: 8px; }
.note { color: var(--muted); font-size: 0.9rem; margin: 10px 0 0; }
.probe { margin-top: 22px; padding-left: 44px; }
.probe:first-of-type { margin-top: 14px; }
.probe-label { font-size: 0.95rem; font-weight: 600; margin: 0 0 8px; }
@media (max-width: 640px) { .probe { padding-left: 0; } }
.grid {
  display: grid; gap: 18px; margin-top: 18px;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
}
.shot { margin: 0; }
.shot img {
  width: 100%; height: auto; display: block; border-radius: 10px;
  border: 1px solid var(--line); background: var(--card);
}
.missing {
  border: 1px dashed var(--line); border-radius: 10px; padding: 32px 12px;
  text-align: center; color: var(--muted); font-size: 0.85rem;
}
figcaption { font-size: 0.82rem; margin-top: 7px; color: var(--muted); }
figcaption a { color: var(--accent); text-decoration: none; }
figcaption a:hover { text-decoration: underline; }
a:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 3px; }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
.empty { color: var(--muted); font-style: italic; }
.directions { border-top: 1px solid var(--line); padding-top: 36px; }
.directions h2 { font-size: 1.2rem; margin: 0 0 18px; }
.directions ol { margin: 0; padding-left: 1.1rem; }
.directions li { margin-bottom: 22px; }
.directions h3 { font-size: 1rem; margin: 0 0 5px; }
.directions p { margin: 0; max-width: 68ch; }
.refs { color: var(--muted); font-size: 0.85rem; margin-top: 5px !important; }
.verdict {
  margin-top: 26px; padding: 13px 15px; border-left: 3px solid var(--line);
  color: var(--muted); font-size: 0.93rem;
}
@media (max-width: 640px) {
  .wrap { padding: 32px 16px 64px; }
  .grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
}
"""


def build(data):
    meta = []
    for key, label in (("altitude", "Altitude"), ("tool", "Tool"),
                       ("platform", "Platform"), ("source", "Source")):
        if data.get(key):
            meta.append(f"<li>{e(label)}: {e(data[key])}</li>")

    sweeps = "".join(render_sweep(i, s) for i, s in enumerate(data.get("sweeps", []), 1))
    directions = render_directions(data.get("directions"), data.get("verdict"))
    title = data.get("title") or "Reference sweep"

    return f"""<title>{e(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600&display=swap">
<style>{CSS}</style>
<div class="wrap">
  <header>
    <h1>{e(title)}</h1>
    <p class="problem">{e(data.get('problem'))}</p>
    <ul class="meta">{''.join(meta)}</ul>
  </header>
  {sweeps}
  {directions}
</div>"""


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    if not shutil.which("curl"):
        print("curl not found on PATH; images cannot be embedded.", file=sys.stderr)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    screens = []
    for sweep in data.get("sweeps", []):
        probes = sweep.get("probes") or [sweep]
        for probe in probes:
            screens.extend(probe.get("screens", []))
    urls = [s.get("image_url") for s in screens]

    if urls:
        with ThreadPoolExecutor(max_workers=8) as pool:
            for screen, uri in zip(screens, pool.map(fetch_data_uri, urls)):
                screen["_data_uri"] = uri

    ok = sum(1 for s in screens if s.get("_data_uri"))
    with open(sys.argv[2], "w") as f:
        f.write(build(data))

    size_mb = len(open(sys.argv[2], "rb").read()) / 1_000_000
    print(f"Wrote {sys.argv[2]} — {ok}/{len(screens)} images embedded, {size_mb:.1f} MB")
    if ok < len(screens):
        print("Some images could not be fetched; those slots show a placeholder.")
    if size_mb > 15:
        print("WARNING: near the 16 MB artifact limit. Reduce the number of screens per sweep.")


if __name__ == "__main__":
    main()
