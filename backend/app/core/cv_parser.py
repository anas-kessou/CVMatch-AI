import fitz # PyMuPDF
import docx
import io

def parse_cv(file_bytes: bytes, filename: str) -> str:
    text = ""
    if filename.lower().endswith(".pdf"):
        doc = fitz.open("pdf", file_bytes)
        for page in doc:
            text += page.get_text()
    elif filename.lower().endswith(".docx"):
        doc = docx.Document(io.BytesIO(file_bytes))
        for para in doc.paragraphs:
            text += para.text + "\n"
    
    return text.strip()
