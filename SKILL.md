---
name: kindle-publish
description: Typeset a content manifest into a Kindle-native PDF (and optional EPUB), generate an AI cover, verify the render, and push it to a Kindle device by Send-to-Kindle email. Triggers on "推送到 kindle / push to kindle / kindle publish / 生成 kindle 文档 / sync to kindle". Owns style, naming, and delivery only; content collection stays with the caller.
---

# kindle-publish

Turn prepared content into a verified, Kindle-ready document and deliver it.
This skill owns three specs — style, data contract, delivery. It does not
collect, select, or schedule content; the caller supplies a manifest.

## Steps

1. **Read the manifest.** The caller supplies content that satisfies
   `references/content-schema.md`. Reject a manifest that misses a required
   field or has no `sources`; ask the caller once for the gap.
2. **Name the deliverable.** Apply the naming spec in
   `references/content-schema.md` «Titling and naming». The output filename is
   the Kindle library title; never ship a working filename.
3. **Generate the cover** with the host image tool, using the cover brief
   rules in `references/style-spec.md` «Cover».
4. **Fill `templates/kindle-doc.html`.** CSS stays untouched; content only.
   Figures follow `references/style-spec.md` «Figures».
5. **Render and verify.** WeasyPrint to PDF, then run the checks in
   `references/delivery.md` «Verification». A failed check is a draft defect;
   fix and re-render before delivery.
6. **Deliver.** Follow `references/delivery.md` «Send». Recipient and sender
   come from `config.yaml` next to this file; never hardcode an address.

## EPUB branch

When the caller requests adjustable fonts (`output: epub` or `both`), also
build the pandoc EPUB path in `references/delivery.md` «EPUB». PDF stays the
default deliverable.

## Boundaries

- No content pipeline: sourcing, summarising, and scheduling belong to the caller.
- No cron or automation setup: schedulers call this skill, not the reverse.
- One manifest, one document, one delivery.
