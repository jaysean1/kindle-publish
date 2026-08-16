---
name: kindle-publish
description: Publish prepared content or a local file to Kindle. Typeset manifests, sync supported documents, convert MOBI prose books, and rebuild image-heavy comics as Kindle-safe grayscale PDFs before Send-to-Kindle delivery. Triggers on "推送到 kindle / push to kindle / kindle publish / 生成 kindle 文档 / sync to kindle / 传到 kindle / MOBI 漫画".
---

# kindle-publish

Publish a prepared manifest or local file as a verified Kindle document.
This skill owns formatting, conversion, validation, and delivery. It does not
collect, select, or schedule content.

## Route first

- **Prepared content manifest:** follow «Manifest publishing» below.
- **Local PDF, EPUB, DOCX, HTML, MOBI, AZW, AZW3, or CBZ:** read
  `references/local-file-sync.md` and select its route table.
- **Image-heavy comic:** always use the comic route. A successful generic
  EPUB conversion is not evidence that an older Kindle can open the book.

## Manifest publishing

1. **Read the manifest.** Require the fields in
   `references/content-schema.md`. Reject missing required fields or an empty
   `sources` list; ask once for the gap.
2. **Name the deliverable.** Apply `references/content-schema.md` «Titling
   and naming». The filename is the old-firmware library title.
3. **Generate the cover** with the host image tool. Apply
   `references/style-spec.md` «Cover».
4. **Fill `templates/kindle-doc.html`.** Keep CSS unchanged. Apply
   `references/style-spec.md` «Figures».
5. **Render and verify.** Use WeasyPrint, then run
   `references/delivery.md` «Verification». Fix every failed check.
6. **Deliver.** Use `references/delivery.md` «Send». Read recipient and sender
   from `config.yaml`; never hardcode an address.

## Local file publishing

1. Preserve the source.
2. Select email, web upload, prose conversion, or comic conversion from
   `references/local-file-sync.md`.
3. Verify the resulting file before delivery.
4. For web delivery, wait for Amazon status **In library**. Report
   **Processing** as incomplete.
5. Ask the user to open the file on the device when compatibility is the
   reason for conversion.

## EPUB branch

When the caller requests adjustable fonts (`output: epub` or `both`), also
build the pandoc EPUB path in `references/delivery.md` «EPUB». PDF stays the
default deliverable.

## Boundaries

- No content pipeline: sourcing, summarising, and scheduling belong to the caller.
- No cron setup: schedulers call this skill, not the reverse.
- Preserve every local source file.
- A requested delivery is approval for that exact verified file. Confirm again
  when conversion creates multiple parts or changes the requested destination.
