import pdfplumber
import docx
import os
from io import BytesIO

# This function receives the uploaded file from FastAPI
async def extract_text_from_file(uploaded_file) -> str:
    filename = uploaded_file.filename
    file_ext = os.path.splitext(filename)[-1].lower()
    file_bytes = await uploaded_file.read()

    if file_ext == ".pdf":
        return extract_text_from_pdf(file_bytes)
    elif file_ext == ".docx":
        return extract_text_from_docx(file_bytes)
    else:
        return "Unsupported file type."

# PDF extractor using pdfplumber
def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text

# DOCX extractor using python-docx
def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])
