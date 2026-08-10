"""
Extracts plain text from raw file bytes based on source type.

PDF extraction is per-page and tolerant of individual page failures - if
a handful of pages in a large PDF fail to parse, we still return the text
we could extract and flag which pages failed, rather than discarding the
whole document (the partial-failure handling requirement from the
requirements review).
"""
import io

from bs4 import BeautifulSoup
from docx import Document as DocxDocument
from pypdf import PdfReader


class ExtractionResult:
    def __init__(self, text: str, failed_pages: list[int] | None = None):
        self.text = text
        self.failed_pages = failed_pages or []

    @property
    def is_partial(self) -> bool:
        return len(self.failed_pages) > 0


def extract_text(*, content: bytes, source_type: str) -> ExtractionResult:
    if source_type in ("txt", "md", "paste"):
        return ExtractionResult(text=content.decode("utf-8", errors="replace"))
    if source_type == "pdf":
        return _extract_pdf(content)
    if source_type == "docx":
        return _extract_docx(content)
    if source_type == "url":
        return _extract_html(content)
    return ExtractionResult(text=content.decode("utf-8", errors="replace"))


def _extract_pdf(content: bytes) -> ExtractionResult:
    reader = PdfReader(io.BytesIO(content))
    texts: list[str] = []
    failed_pages: list[int] = []
    for i, page in enumerate(reader.pages):
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            failed_pages.append(i + 1)
    return ExtractionResult(text="\n\n".join(texts), failed_pages=failed_pages)


def _extract_docx(content: bytes) -> ExtractionResult:
    doc = DocxDocument(io.BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return ExtractionResult(text="\n\n".join(paragraphs))


def _extract_html(content: bytes) -> ExtractionResult:
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()
    text = soup.get_text(separator="\n\n")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return ExtractionResult(text="\n\n".join(lines))
