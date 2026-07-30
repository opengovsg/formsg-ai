# Product skills

Product management workflows. No per-repo setup required — available immediately after installing the plugin.

These skills operate on a product's own repository (for example the products.open.gov.sg content repo), so run them from that checkout rather than from here.

## Skills

| Skill | Description |
|-------|-------------|
| [`/highlights`](highlights/SKILL.md) | Scan a product's Slack channel, GitHub repo and Notion pages for a quarter's shipped work, then draft the `CHANGELOG.md` entry in that product's existing format |
| [`/reportcard`](reportcard/SKILL.md) | Add a quarter's team, cost and metric values to an OGP product report card by auditing the last recorded quarter, then asking the PM for each missing number |

## Order

Run them in this order — `/highlights` writes the story, `/reportcard` fills in
the numbers:

```
/highlights <product>   →  CHANGELOG.md entry
/reportcard <product>   →  reportcard.yml values
```

They are separate because the jobs differ: `/highlights` is broad retrieval and
judgment across several sources and wants a strong model, while `/reportcard` is
a mechanical append that runs in seconds and works offline.
