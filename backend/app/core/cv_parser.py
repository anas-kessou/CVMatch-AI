from pathlib import Path
from typing import Optional
import logging

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
import pymupdf4llm

logger = logging.getLogger(__name__)

class CVParser:
    """
    Service de parsing moderne 2026
    Priorité : Docling 2.x → Fallback : pymupdf4llm
    """
    
    def __init__(self):
        # Configuration optimisée pour les CVs (layout-aware + tableaux + OCR)
        pdf_options = PdfPipelineOptions()
        pdf_options.do_ocr = True
        pdf_options.do_table_structure = True
        pdf_options.table_structure_options.do_cell_matching = True
        
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: pdf_options,
            }
        )
        logger.info("CVParser initialized with Docling 2.x + fallback pymupdf4llm")

    async def parse_to_markdown(self, file_path: str | Path) -> str:
        """
        Parse un CV (PDF ou DOCX) et retourne du Markdown structuré de haute qualité.
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"CV file not found: {file_path}")

        try:
            logger.info(f"Parsing {file_path.name} using Docling 2.x...")
            result = self.converter.convert(str(file_path))
            markdown = result.document.export_to_markdown()

            if markdown and len(markdown.strip()) > 100:
                logger.info(f"✅ Docling parsing successful ({len(markdown)} chars)")
                return markdown
            else:
                raise ValueError("Docling returned empty or too short content")

        except Exception as e:
            logger.warning(f"Docling failed for {file_path.name}: {str(e)}. Using fallback...")
            return self._fallback_parse(file_path)

    def _fallback_parse(self, file_path: Path) -> str:
        """Fallback rapide et fiable"""
        try:
            if file_path.suffix.lower() == ".pdf":
                markdown = pymupdf4llm.to_markdown(str(file_path))
                logger.info(f"✅ Fallback pymupdf4llm successful ({len(markdown)} chars)")
                return markdown
            else:
                # DOCX fallback (à améliorer plus tard avec python-docx + markdown)
                raise NotImplementedError(f"Direct DOCX parsing not yet implemented. Got: {file_path.suffix}")
        except Exception as e:
            logger.error(f"Fallback parsing failed for {file_path}: {e}")
            raise RuntimeError(f"Failed to parse CV {file_path.name}") from e