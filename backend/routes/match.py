from fastapi import APIRouter, UploadFile, File, Form
from utils.parser import extract_text_from_file
from utils.prompts import (
    get_resume_analysis_prompt,
    call_gemini,
    generate_job_description_if_needed,
    get_cover_letter_prompt
)

router = APIRouter()

@router.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...)
):
    # Extract resume text from uploaded file
    resume_text = await extract_text_from_file(resume)

    # Expand short job description if needed
    job_description, was_auto_generated = generate_job_description_if_needed(job_description)

    # Build the prompt
    prompt = get_resume_analysis_prompt(resume_text, job_description)
    
    # Generate cover letter prompt
    cover_prompt = get_cover_letter_prompt(resume_text, job_description)
    cover_letter_result = call_gemini(cover_prompt)

    # Send prompt to Gemini for analysis
    result = call_gemini(prompt, was_auto_generated=was_auto_generated)

    # Include metadata so frontend can show a message
    result["auto_generated"] = was_auto_generated

    # Generate cover letter from resume + job description
    cover_prompt = get_cover_letter_prompt(resume_text, job_description)
    cover_letter = call_gemini(cover_prompt)

    # Attach cover letter text to result
    if isinstance(cover_letter, dict):
        result["cover_letter"] = cover_letter.get("raw_response", "")
    else:
        result["cover_letter"] = cover_letter
    
    # Return result to frontend
    return {"result": result}
