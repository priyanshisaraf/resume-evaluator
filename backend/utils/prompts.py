import os
import json
import requests
from dotenv import load_dotenv

# Load environment variable from .env
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Build the structured evaluation prompt
def get_resume_analysis_prompt(resume_text: str, job_desc: str) -> str:
    return f"""
You are a resume evaluation assistant.

Compare the resume and job description and return ONLY valid JSON with:
- "score" (int from 0 to 100): Resume match score
- "missing_skills" (list of strings): Skills missing in the resume but required in the job
- "suggestions" (list of strings): Suggest how to improve resume bullet points tailored to the job with an example
- "justification" (string): One-paragraph explanation for why this score was given

Only return valid JSON. No extra commentary.

Resume:
\"\"\"{resume_text}\"\"\"

Job Description:
\"\"\"{job_desc}\"\"\"
"""

# Call Gemini via REST API and parse JSON output
def call_gemini(prompt: str, was_auto_generated: bool = False) -> dict:
    print("Sending prompt via Gemini REST API...")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }

    body = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        data = response.json()

        if "candidates" in data:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            print("Gemini Raw Output:\n", text)

            if text.strip().startswith("```json"):
                text = text.replace("```json", "").replace("```", "").strip()

            try:
                parsed = json.loads(text)
                print("Parsed JSON successfully")
                return parsed
            except json.JSONDecodeError as e:
                print("JSON parse failed:", str(e))
        else:
            print("Gemini Error:", data)

    except Exception as e:
        print("Request failed:", str(e))

    # Fallback: General skills if auto-generated JD was used
    fallback_skills = ["Communication", "Teamwork", "Problem-Solving", "Time Management"]
    return {
        "score": 0,
        "missing_skills": fallback_skills if was_auto_generated else [],
        "suggestions": [],
        "justification": "Response could not be parsed. Displaying general skills.",
        "raw_response": "Failed to process response."
    }

# Generate job description from job title if too short
def generate_job_description_if_needed(job_desc: str) -> (str, bool):
    if len(job_desc.split()) < 20:
        print("Job description too short \u2014 generating realistic one via Gemini.")
        expansion_prompt = f"Write a realistic 3-5 sentence job description for the role: '{job_desc}'."

        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": expansion_prompt}]}]}
            )
            data = response.json()
            full_jd = data["candidates"][0]["content"]["parts"][0]["text"]
            print("Job description generated.")
            return full_jd, True
        except Exception as e:
            print(" description generation failed:", e)
            return job_desc, False
    else:
        return job_desc, False

# # Generate cover letter prompt
def get_cover_letter_prompt(resume_text: str, job_desc: str) -> str:
    return f"""
You are a helpful assistant that writes personalized cover letters.

Using the information from this resume and job description, write a concise, professional cover letter tailored for the job.

Respond with plain text (no markdown or formatting).

Resume:
\"\"\"{resume_text}\"\"\"

Job Description:
\"\"\"{job_desc}\"\"\"
"""
