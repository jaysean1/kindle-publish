# kindle-publish

An agent skill that publishes prepared content and local files to Kindle.
It supports two main paths:

- Manifest → Kindle-native PDF (optional EPUB), AI cover, visual checks, delivery.
- Local file → direct sync or safe conversion. Image-heavy MOBI/EPUB/CBZ comics
  rebuild as grayscale, single-image-page PDFs for older Kindle devices.

Files:

- Style, naming, local-file routing, and delivery specs: `references/`
- Frozen page template (91×122mm, no background, thin rules): `templates/kindle-doc.html`
- Comic converter: `scripts/manga_to_kindle_pdf.py`
- Device address: copy `config.example.yaml` to `config.yaml` (git-ignored)

Quick comic conversion:

```bash
python3 scripts/manga_to_kindle_pdf.py book.mobi \
  --output-dir output --title "书名-卷01" --author "作者"
```

The source file stays unchanged. The script verifies page order through first,
middle, and last previews and splits only above the web upload threshold.

Content collection and scheduling are out of scope. Verified on a 6" Kindle
Paperwhite, 2026-08.
