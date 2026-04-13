from __future__ import annotations

from io import BytesIO

import fitz
from docx import Document

class CvParserService:
    """Extract text from PDF/DOCX files."""

    def extract_text(self, filename: str, content: bytes) -> str:
        lowered = filename.lower()
        if lowered.endswith(".pdf"):
            return self._extract_pdf(content)
        if lowered.endswith(".docx"):
            return self._extract_docx(content)
        raise ValueError(f"Unsupported format for file: {filename}")

    @staticmethod
    def _extract_pdf(content: bytes) -> str:
        with fitz.open(stream=content, filetype="pdf") as document:
            pages = [page.get_text("text") for page in document]
        return "\n".join(page.strip() for page in pages if page.strip())

    @staticmethod
    def _extract_docx(content: bytes) -> str:
        doc = Document(BytesIO(content))
        paragraphs = [paragraph.text.strip() for paragraph in doc.paragraphs]
        return "\n".join(paragraph for paragraph in paragraphs if paragraph)
