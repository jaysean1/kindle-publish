# kindle-publish

An agent skill that typesets a content manifest into a Kindle-native PDF
(optional EPUB), generates an AI cover, verifies the render, and delivers it
by Send-to-Kindle email.

- Style, naming, and delivery specs: `references/`
- Frozen page template (91×122mm, no background, thin rules): `templates/kindle-doc.html`
- Device address: copy `config.example.yaml` to `config.yaml` (git-ignored)

Content collection is out of scope: a caller (daily digest pipeline, ad-hoc
article task) prepares the manifest defined in `references/content-schema.md`
and invokes this skill.

Verified on a 6" Kindle Paperwhite, 2026-08.
