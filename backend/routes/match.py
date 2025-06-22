from fastapi import APIRouter, UploadFile, File, Form
from utils.prompts import (
    get_resume_analysis_prompt,
    call_gemini,
    generate_job_description_if_needed
)
import time
import os
from io import BytesIO
import docx
import fitz  # PyMuPDF for faster PDF parsing

router = APIRouter()

# Optimized text extractor
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

# Faster PDF text extractor using PyMuPDF
def extract_text_from_pdf_faster(file_bytes: bytes) -> str:
    doc = fitz.open(stream=file_bytes, filetype="pdf")
    text = "\n".join([page.get_text() for page in doc])
    return text if text.strip() else "Could not extract readable text from PDF."

# DOCX extractor using python-docx
def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(BytesIO(file_bytes))
    text = "\n".join([para.text for para in doc.paragraphs])
    return text if text.strip() else "Could not extract readable text from DOCX."

# Utility function to truncate resume text
def truncate_text(text: str, max_words: int = 1000) -> str:
    words = text.split()
    return ' '.join(words[:max_words])

@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    # Step 1: Extract resume text from uploaded file
    start = time.time()
    resume_text = await extract_text_from_file(resume)
    print("Resume parsed in", round(time.time() - start, 2), "seconds")

    # Step 2: Truncate long resumes
    resume_text = truncate_text(resume_text)

    # Step 3: Expand short job description if needed
    job_description, was_auto_generated = generate_job_description_if_needed(job_description)

    # Step 4: Build the prompt
    prompt = get_resume_analysis_prompt(resume_text, job_description)

    # Step 5: Send prompt to Gemini for analysis
    start = time.time()
    result = call_gemini(prompt, was_auto_generated=was_auto_generated)
    print("Gemini response time:", round(time.time() - start, 2), "seconds")

    # Step 6: Include metadata so frontend can show a message
    result["auto_generated"] = was_auto_generated

    # Step 7: Return result to frontend
    return {"result": result}
