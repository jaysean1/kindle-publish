# Delivery — render, verify, send

## Render

```bash
python3 -c "import weasyprint; weasyprint.HTML('filled.html').write_pdf('<final-name>.pdf')"
```

WeasyPrint needs `pango` (`brew install pango`) and the `weasyprint pypdf`
Python packages. Name the output per the naming spec in
`content-schema.md` before sending; the filename is the library title.

## Verification

Run both before any send; a failure is a draft defect.

1. **Visual pass** — export page images (kami's
   `scripts/build.py --check-visual <pdf>` when kami is installed, else
   pymupdf) and view every page for: fallback glyphs, heavy lines (a ≥ 2pt
   decorative line means a clamped value), figure label overlap, stranded
   headings, sparse body pages.
2. **Font pass** — confirm CJK body ideographs drew in the serif family
   (kami `--check-fonts`, or pymupdf span table). A silent sans
   substitution passes an eyeball check; the deterministic pass settles it.

## Send

Recipient, sender, and defaults live in `config.yaml` next to `SKILL.md`:

```yaml
kindle_email: "xxx@kindle.com"   # device address, amazon.com/myk
approved_sender: "you@gmail.com" # must be on the Amazon approved list
default_output: pdf
```

Send with the gmail skill (dry-run first, as that skill requires):

```bash
uv run send_email.py --html body.html --to <kindle_email> \
  --subject "<per naming spec>" --attachment <final-name>.pdf
```

Delivery facts learned the hard way:

- An unapproved sender is **silently dropped** — no bounce. First failure
  to arrive: check the approved list at amazon.com/myk before anything else.
- Attachment limit 50MB; device needs Wi-Fi plus a manual sync
  (⋮ → 同步我的 Kindle) to pull promptly.
- Old-firmware library tiles ignore embedded covers; the filename is the
  visible identity (hence the naming spec).

## EPUB

For `output: epub | both`: rasterise SVG figures to PNG, write the body as
Markdown, then:

```bash
pandoc content.md --epub-cover-image=cover.png --toc --toc-depth=1 -o <final-name>.epub
```

EPUB converts to a reflowable format on Amazon's side — the reader can
adjust font size and family, at the cost of the fixed typography. PDF keeps
the typography and fixes the size. Ship what the manifest asks.
