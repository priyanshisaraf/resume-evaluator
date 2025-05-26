from fastapi import APIRouter, UploadFile, File, Form
from utils.parser import extract_text_from_file
from utils.prompts import (
    get_resume_analysis_prompt,
    call_gemini,
    generate_job_description_if_needed
)

router = APIRouter()

@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    # Step 1: Extract resume text from uploaded file
    resume_text = await extract_text_from_file(resume)

    # Step 2: Expand short job description if needed
    job_description, was_auto_generated = generate_job_description_if_needed(job_description)

    # Step 3: Build the prompt
    prompt = get_resume_analysis_prompt(resume_text, job_description)

    # Step 4: Send prompt to Gemini for analysis
    result = call_gemini(prompt, was_auto_generated=was_auto_generated)

    # Step 5: Include metadata so frontend can show a message
    result["auto_generated"] = was_auto_generated

    # Step 6: Return result to frontend
    return {"result": result}
