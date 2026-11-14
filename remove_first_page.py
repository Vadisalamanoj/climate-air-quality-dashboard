#!/usr/bin/env python3
"""Remove the first page from a PDF file.

Usage:
    python remove_first_page.py INPUT.pdf
    python remove_first_page.py INPUT.pdf OUTPUT.pdf
"""

from __future__ import annotations

import sys
from pathlib import Path


def remove_first_page(input_pdf: str | Path, output_pdf: str | Path | None = None) -> Path:
    input_path = Path(input_pdf)
    if not input_path.exists():
        raise FileNotFoundError(f"PDF not found: {input_path}")

    if output_pdf is None:
        output_path = input_path.with_name(f"{input_path.stem}_no_first_page{input_path.suffix}")
    else:
        output_path = Path(output_pdf)

    # Prefer pypdf for a dependency-light approach.
    try:
        from pypdf import PdfReader, PdfWriter

        reader = PdfReader(str(input_path))
        writer = PdfWriter()

        for page_index, page in enumerate(reader.pages):
            if page_index == 0:
                continue
            writer.add_page(page)

        if len(writer.pages) == 0:
            raise ValueError(f"The PDF has no pages left after removing the first page: {input_path}")

        with output_path.open("wb") as f:
            writer.write(f)

        return output_path
    except Exception:
        # Fallback to PyMuPDF if installed.
        try:
            import fitz

            doc = fitz.open(str(input_path))
            if doc.page_count <= 1:
                raise ValueError(f"The PDF only has one page: {input_path}")

            new_doc = fitz.open()
            for page_index in range(1, doc.page_count):
                new_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)

            new_doc.save(str(output_path))
            new_doc.close()
            doc.close()
            return output_path
        except Exception as exc:
            raise RuntimeError(
                "Could not remove the first page. Install one of these: pypdf or PyMuPDF."
            ) from exc


if __name__ == "__main__":
    if len(sys.argv) not in {2, 3}:
        print("Usage: python remove_first_page.py INPUT.pdf [OUTPUT.pdf]", file=sys.stderr)
        raise SystemExit(2)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2] if len(sys.argv) == 3 else None

    try:
        output = remove_first_page(input_pdf, output_pdf)
        print(f"Saved: {output}")
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
