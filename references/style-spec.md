# Style spec — Kindle-native typography

Verified on a Kindle Paperwhite (6", grayscale, old firmware) on 2026-08-15.
The template `templates/kindle-doc.html` already encodes all of this; this
file explains the values so a change stays deliberate.

## Page geometry

| Property | Value | Reason |
|---|---|---|
| Page size | 91mm × 122mm | Paperwhite screen size; full-screen PDF shows true type size |
| Margins | 6 / 6 / 7 / 6 mm | Tight; the device bezel is the real margin |
| Body type | 8.5pt, line-height 1.6, letter-spacing 0.2pt | Reads like 11pt print at device scale |

## Colour

- Background: **none**. No parchment, no ivory card fills, no tinted table
  headers. A printed background differs from the device's native tone and
  shows as banding at page edges.
- Ink: near-black `#141413` body, warm grays `#504e49` / `#6b6a64` for
  secondary text.
- Accent: ink-blue `#1B365D` only, on numbers, key phrases, chapter marks,
  and figure strokes. At most 2 accents per line.

## Line weights

Grayscale e-ink renders any decorative line ≥ 2pt as a heavy black bar.

| Element | Weight |
|---|---|
| TOC dotted leader | 0.5pt dotted `#c9c7bd` |
| Table rules | 0.5–0.7pt solid |
| Heading accent bar | 2pt (the one allowed thick mark) |
| Blockquote / callout left rule | 1.2pt |

## Fonts

- CJK: TsangerJinKai02 (bundled with kami), fallback Source Han Serif SC →
  Songti SC. Verify with a font check after render; a silent sans
  substitution reads flat without visible fallback boxes.
- Latin/numeric: same serif stack.

## Cover

- Generate with the host image tool (for example `codex_generate_image`).
- Portrait 2:3, full-bleed on page 1 of the PDF.
- Brief skeleton: warm parchment field is allowed **inside the artwork**
  (it is an image, not a page background); ink-blue `#1B365D` single accent;
  thin single-line geometric strokes; no gradients, shadows, or 3D; large
  serif title readable at grayscale thumbnail size.
- Title text inside the cover must match the manifest `title` and `date`.

## Figures

- Author as inline SVG in the template, white/transparent background,
  `fill="none"` boxes, strokes `#1B365D` (accent flow) and `#504e49`
  (secondary), labels in the serif stack.
- For the EPUB branch, rasterise each SVG to PNG (Chrome headless
  screenshot at 2× viewBox) because Kindle EPUB conversion drops SVG.
- Every figure carries a `figcaption` that states the reading, not the
  data range.
