import os
from io import BytesIO
import docx
import fitz

async def extract_text_from_file(uploaded_file) -> str:
    filename = uploaded_file.filename
    file_ext = os.path.splitext(filename)[-1].lower()
    file_bytes = await uploaded_file.read()

    if file_ext == ".pdf":
        return extract_text_from_pdf_faster(file_bytes)
    elif file_ext == ".docx":
        return extract_text_from_docx(file_bytes)
    else:
        return "Unsupported file type."

def extract_text_from_pdf_faster(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])
    return text if text.strip() else "Could not extract readable text from PDF."

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(BytesIO(file_bytes))
    text = "\n".join([para.text for para in doc.paragraphs])
    return text if text.strip() else "Could not extract readable text from DOCX."

def truncate_text(text: str, max_words: int = 1000) -> str:
    words = text.split()
    return ' '.join(words[:max_words])
