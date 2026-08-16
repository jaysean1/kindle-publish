#!/usr/bin/env python3
"""Convert an image-heavy book to a Kindle-safe grayscale PDF."""

from __future__ import annotations

import argparse
import io
import math
import posixpath
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree as ET

import img2pdf
from PIL import Image, ImageOps

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"}


def natural_key(value: str) -> list[object]:
    """Sort names by their numeric parts."""
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", value)]


def convert_calibre_book(source: Path, work_dir: Path) -> Path:
    """Convert a Kindle book to an intermediate EPUB."""
    converter = shutil.which("ebook-convert")
    if not converter:
        app_path = Path("/Applications/calibre.app/Contents/MacOS/ebook-convert")
        converter = str(app_path) if app_path.exists() else None
    if not converter:
        raise SystemExit("Missing Calibre ebook-convert. Install Calibre first.")
    target = work_dir / f"{source.stem}-intermediate.epub"
    subprocess.run([converter, str(source), str(target)], check=True)
    return target


def epub_spine_images(epub_path: Path) -> list[tuple[str, bytes]]:
    """Read EPUB images in spine order."""
    with zipfile.ZipFile(epub_path) as archive:
        names = set(archive.namelist())
        try:
            container = ET.fromstring(archive.read("META-INF/container.xml"))
            rootfile = next(node for node in container.iter() if node.tag.endswith("rootfile"))
            opf_name = rootfile.attrib["full-path"]
            opf = ET.fromstring(archive.read(opf_name))
            opf_dir = posixpath.dirname(opf_name)
            manifest: dict[str, str] = {}
            spine: list[str] = []
            for node in opf.iter():
                if node.tag.endswith("item") and "id" in node.attrib and "href" in node.attrib:
                    manifest[node.attrib["id"]] = posixpath.normpath(posixpath.join(opf_dir, unquote(node.attrib["href"])))
                elif node.tag.endswith("itemref") and "idref" in node.attrib:
                    spine.append(node.attrib["idref"])

            ordered: list[str] = []
            for item_id in spine:
                page_name = manifest.get(item_id)
                if not page_name or page_name not in names:
                    continue
                page_dir = posixpath.dirname(page_name)
                page = ET.fromstring(archive.read(page_name))
                for node in page.iter():
                    src = node.attrib.get("src")
                    if src and Path(src).suffix.lower() in IMAGE_SUFFIXES:
                        image_name = posixpath.normpath(posixpath.join(page_dir, unquote(src)))
                        if image_name in names and image_name not in ordered:
                            ordered.append(image_name)
            if ordered:
                return [(name, archive.read(name)) for name in ordered]
        except (KeyError, StopIteration, ET.ParseError):
            pass

        fallback = sorted(
            (name for name in names if Path(name).suffix.lower() in IMAGE_SUFFIXES),
            key=natural_key,
        )
        return [(name, archive.read(name)) for name in fallback]


def archive_images(source: Path) -> list[tuple[str, bytes]]:
    """Read image pages from EPUB or CBZ."""
    if source.suffix.lower() == ".epub":
        return epub_spine_images(source)
    with zipfile.ZipFile(source) as archive:
        names = sorted(
            (name for name in archive.namelist() if Path(name).suffix.lower() in IMAGE_SUFFIXES),
            key=natural_key,
        )
        return [(name, archive.read(name)) for name in names]


def optimise_pages(
    images: list[tuple[str, bytes]],
    page_dir: Path,
    width: int,
    height: int,
    quality: int,
) -> list[Path]:
    """Create baseline grayscale JPEG pages."""
    page_dir.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    for index, (_, data) in enumerate(images, start=1):
        with Image.open(io.BytesIO(data)) as source_image:
            image = source_image.convert("L")
            image = ImageOps.autocontrast(image, cutoff=(0.25, 0.25))
            image.thumbnail((width, height), Image.Resampling.LANCZOS)
            canvas = Image.new("L", (width, height), 255)
            canvas.paste(image, ((width - image.width) // 2, (height - image.height) // 2))
            output = page_dir / f"{index:04d}.jpg"
            canvas.save(output, "JPEG", quality=quality, optimize=True, progressive=False)
            outputs.append(output)
        if index % 25 == 0 or index == len(images):
            print(f"Optimised {index}/{len(images)} pages")
    return outputs


def build_pdf(pages: list[Path], output: Path, title: str, author: str) -> None:
    """Build a fixed-size image PDF without recompression."""
    layout = img2pdf.get_layout_fun(
        (img2pdf.mm_to_pt(91), img2pdf.mm_to_pt(122)),
        fit=img2pdf.FitMode.into,
    )
    with output.open("wb") as target:
        target.write(
            img2pdf.convert(
                [str(page) for page in pages],
                layout_fun=layout,
                title=title,
                author=author,
                producer="kindle-publish",
            )
        )


def split_large_pdf(pdf_path: Path, threshold_mb: int) -> list[Path]:
    """Split a PDF only when it exceeds the web upload threshold."""
    threshold = threshold_mb * 1024 * 1024
    if pdf_path.stat().st_size <= threshold:
        return [pdf_path]
    from pypdf import PdfReader, PdfWriter

    reader = PdfReader(str(pdf_path))
    ratio = threshold / pdf_path.stat().st_size
    pages_per_part = max(1, math.floor(len(reader.pages) * ratio * 0.9))
    outputs: list[Path] = []
    for part_index, start in enumerate(range(0, len(reader.pages), pages_per_part), start=1):
        writer = PdfWriter()
        for page in reader.pages[start : start + pages_per_part]:
            writer.add_page(page)
        output = pdf_path.with_name(f"{pdf_path.stem}-part-{part_index:02d}.pdf")
        with output.open("wb") as target:
            writer.write(target)
        outputs.append(output)
    return outputs


def write_previews(pdf_path: Path, preview_dir: Path) -> None:
    """Render the first, middle, and last pages for visual review."""
    try:
        import fitz
    except ImportError:
        print("Preview skipped: install pymupdf")
        return
    preview_dir.mkdir(parents=True, exist_ok=True)
    document = fitz.open(pdf_path)
    indexes = sorted({0, len(document) // 2, len(document) - 1})
    for page_index in indexes:
        page = document[page_index]
        pixmap = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
        pixmap.save(preview_dir / f"page-{page_index + 1:04d}.png")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="MOBI, AZW, AZW3, EPUB, or CBZ input")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--title", help="PDF title. Defaults to the source name.")
    parser.add_argument("--author", default="Unknown")
    parser.add_argument("--width", type=int, default=1072)
    parser.add_argument("--height", type=int, default=1448)
    parser.add_argument("--quality", type=int, default=82)
    parser.add_argument("--split-threshold-mb", type=int, default=180)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = args.source.expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"Input not found: {source}")
    if source.suffix.lower() not in {".mobi", ".azw", ".azw3", ".epub", ".cbz"}:
        raise SystemExit("Supported inputs: MOBI, AZW, AZW3, EPUB, CBZ")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    title = args.title or source.stem
    with tempfile.TemporaryDirectory(prefix="kindle-manga-") as temp_name:
        work_dir = Path(temp_name)
        archive = (
            convert_calibre_book(source, work_dir)
            if source.suffix.lower() in {".mobi", ".azw", ".azw3"}
            else source
        )
        images = archive_images(archive)
        if not images:
            raise SystemExit("No image pages found")
        page_dir = args.output_dir / "optimised-pages"
        if page_dir.exists():
            shutil.rmtree(page_dir)
        pages = optimise_pages(images, page_dir, args.width, args.height, args.quality)

    output = args.output_dir / f"{title}-Kindle灰階版.pdf"
    build_pdf(pages, output, title, args.author)
    write_previews(output, args.output_dir / "pdf-preview")
    deliverables = split_large_pdf(output, args.split_threshold_mb)
    print(f"Full PDF: {output} ({output.stat().st_size / 1024 / 1024:.1f} MB, {len(pages)} pages)")
    for deliverable in deliverables:
        print(f"Upload: {deliverable}")


if __name__ == "__main__":
    main()
