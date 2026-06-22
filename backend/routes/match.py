import time

from fastapi import APIRouter, File, Form, HTTPException, Response, UploadFile
from starlette.concurrency import run_in_threadpool

from utils.parser import extract_text_from_file, truncate_text
from utils.prompts import (
    GeminiAPIError,
    call_gemini,
    get_resume_analysis_prompt,
)


router = APIRouter()


@router.post("/analyze")
async def analyze_resume(
    response: Response,
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required.")

    started = time.time()
    try:
        resume_text = truncate_text(await extract_text_from_file(resume))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read the uploaded resume.") from exc
    finally:
        await resume.close()
    print("Resume parsed in", round(time.time() - started, 2), "seconds")

    try:
        job_description = job_description.strip()
        used_typical_requirements = len(job_description.split()) < 20
        prompt = get_resume_analysis_prompt(resume_text, job_description)
        started = time.time()
        result = await run_in_threadpool(call_gemini, prompt)
        print("Gemini response time:", round(time.time() - started, 2), "seconds")
    except GeminiAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    result["used_typical_requirements"] = used_typical_requirements
    response.headers["Cache-Control"] = "no-store, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return {"result": result}
