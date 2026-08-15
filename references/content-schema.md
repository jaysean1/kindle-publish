# Content schema — the caller's contract

The caller hands this skill one manifest (YAML or JSON). The skill typesets
and delivers it; it never invents content to fill a gap.

## Manifest

```yaml
kind: daily-digest | article | report   # picks wording defaults below
title: "Symphony：把任务看板变成智能体指挥台"   # display title, ≤ 20 CJK chars
subtitle: "OpenAI 智能体编排开源规范"           # one line, ≤ 24 CJK chars, optional
date: "2026-08-15"                       # ISO date, always the content date
author: "Pi Daily Report"
cover_brief: >                           # semantic description for image gen;
  指挥手与机器人乐团,呼应"编排"主题            # style rules come from style-spec.md
sections:                                # ordered chapters
  - heading: "执行摘要"
    tag: "Executive Summary"             # English chapter tag
    body_md: |                           # Markdown body
      ...
    figures:                             # optional
      - caption: "图 1：..."
        svg: |                           # inline SVG, or
        png: path/to/fig.png             # pre-rendered raster
sources:                                 # REQUIRED, ≥ 1 entry
  - "OpenAI, «...», openai.com/..., 2026-08"
output: pdf | epub | both                # default pdf
```

Required: `kind`, `title`, `date`, `author`, `cover_brief`, `sections`,
`sources`. A manifest without `sources` is rejected — no unattributed
content reaches the device.

## Titling and naming

The Kindle library tile shows the **filename**, not the PDF metadata, on
older firmware. Both must therefore carry the same display title.

| Surface | Rule | Example |
|---|---|---|
| Filename | `{title-slug}-{YYYYMMDD}.pdf`, slug from title, CJK allowed | `每日精选-symphony-20260815.pdf` |
| PDF `<title>` / metadata | `{title}` | Symphony：把任务看板变成智能体指挥台 |
| Cover text | `{title}` large + `{subtitle} · {date}` small | 编排的艺术 / Symphony · 2026.08.15 |
| Email subject | `{kind-label} {MMDD} · {title}` | 每日精选 0815 · Symphony |
| HTML `<meta author>` | `{author}` | Pi Daily Report |

`kind` labels: `daily-digest` → 每日精选, `article` → 深度文章, `report` → 专题报告.

Date discipline: one date, from the manifest, everywhere — cover, filename,
subject, footer. Never re-derive it from "today" at render time; the caller
owns the content date.

## Section quality bar

- `heading` ≤ 12 CJK chars; `tag` is 1–3 English words.
- Every factual claim in `body_md` traces to an entry in `sources`.
- Mark a genuine gap `[DATA NEEDED: ...]`; never pad or invent.
- Body pages should render 60–80% full; merge sections that fall short
  rather than stretching them.
