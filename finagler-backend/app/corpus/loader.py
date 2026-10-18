"""Reads corpus files. Only this file may import pypdf."""
from pathlib import Path
from typing import Iterator

from pypdf import PdfReader

SUPPORTED = {".md", ".txt", ".pdf"}


def load_file(path: Path) -> Iterator[tuple[str, int | None]]:
    """Yields (text, page_number). page_number is None for non-PDF files."""
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                yield text, i
    else:
        yield path.read_text(encoding="utf-8", errors="ignore"), None
