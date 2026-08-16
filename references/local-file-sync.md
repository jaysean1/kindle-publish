# Local file sync

Use this branch when the user supplies a local file and asks to put it on a
Kindle. Preserve the source. Write derived files to an explicit task folder.

## Route

| Input | Action | Transport |
|---|---|---|
| PDF, EPUB, DOCX, HTML ≤ 20MB | Send unchanged after a basic open check | Approved email sender |
| Supported file > 20MB and ≤ 200MB | Send unchanged | Amazon Send-to-Kindle web |
| MOBI, AZW, AZW3 prose book | Convert with Calibre to EPUB; verify metadata | Web, or email when small |
| MOBI, AZW, AZW3, EPUB, CBZ image-heavy comic | Run the comic route below | Web |
| Any output > 180MB | Split into numbered parts | Web |

Amazon web supports PDF, DOC, DOCX, TXT, RTF, HTM, HTML, PNG, GIF, JPG,
JPEG, BMP, and EPUB up to 200MB. It does not support MOBI, AZW, or AZW3.
Use 20MB as the email threshold because the sender can impose a lower limit
than Amazon. Stop when Calibre reports DRM; this skill does not remove DRM.

## Comic route

A generic MOBI-to-EPUB conversion can create an EPUB 2 book with one large
RGB image per page, absolute pixel containers, and no fixed-layout metadata.
Amazon can treat that file as reflowable content. Older Kindle devices can
run out of render memory and close the book.

Build a Kindle-safe PDF instead:

```bash
python3 scripts/manga_to_kindle_pdf.py \
  "/path/to/book.mobi" \
  --output-dir "/path/to/output" \
  --title "书名-卷01" \
  --author "作者"
```

The script applies the verified comic contract:

- Source stays unchanged.
- MOBI, AZW, and AZW3 convert to a temporary EPUB through Calibre.
- Images follow EPUB spine order; filename order is the fallback.
- Pages become grayscale baseline JPEG.
- Canvas is 1072×1448 pixels; the page is 91×122mm.
- The PDF contains one image per page and no HTML or CSS.
- JPEG quality is 82; gentle auto-contrast keeps manga line detail.
- First, middle, and last page previews are exported.
- A file above 180MB splits into numbered parts; the full PDF stays local.

Required tools:

```bash
brew install --cask calibre
pip3 install -r requirements.txt --break-system-packages
```

## Comic verification

Before upload, confirm all of these:

1. PDF page count equals the extracted image count.
2. Page size is 91×122mm.
3. The first, middle, and last previews show the correct order and no crop.
4. Each upload file is under 200MB.
5. The filename is a stable library title, not a working name.

## Web upload

Use the `playwright-cli` skill and open:

`https://www.amazon.com/sendtokindle`

1. Reuse an authorised browser session or let the user sign in.
2. Select the verified file or numbered parts.
3. Keep **Add to your library** on.
4. Click **Send** only after the user has requested this exact delivery.
5. Wait until **Recently sent files** reports **In library**. `Processing` is
   not completion.

For a comic, ask the user to open several pages on the device after delivery.
A successful upload does not prove the old Kindle renderer can open the book.
