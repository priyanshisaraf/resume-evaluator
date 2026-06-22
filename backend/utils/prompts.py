import json
import os
from typing import Any

import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


load_dotenv()

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_GEMINI_MODEL = "gemini-3.1-flash-lite"
REQUEST_TIMEOUT = (5, 60)


def _http_session() -> requests.Session:
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("POST",),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


# Reuse TLS connections across analyses instead of creating a session per request.
HTTP_SESSION = _http_session()


class GeminiAPIError(RuntimeError):
    """Raised when Gemini cannot return a usable response."""


def get_resume_analysis_prompt(resume_text: str, job_desc: str) -> str:
    short_description = len(job_desc.split()) < 20
    job_context = (
        "The job input is only a role title or short summary. Infer standard expectations "
        "for that role while clearly avoiding overly specialized assumptions."
        if short_description
        else "Treat the job input as the complete job description."
    )
    return f"""
You are a resume evaluation assistant.

Compare the resume and job description. Score only evidence present in the resume.
Return:
- matched_skills: relevant skills explicitly supported by the resume
- missing_keywords: important job-description terms not evidenced in the resume
- rewritten_bullets: stronger, ATS-friendly resume bullets tailored to the job
- ats_issues: concrete formatting, structure, or wording issues visible in the extracted text
- justification: a concise explanation of the score

Never invent experience, employers, technologies, or results. Preserve the candidate's
facts in rewritten bullets; use a bracketed placeholder such as [X%] when a metric would
help but is not present. Do not report an ATS issue unless the supplied resume text
provides evidence for it.
{job_context}

Resume:
\"\"\"{resume_text}\"\"\"

Job Description:
\"\"\"{job_desc}\"\"\"
"""


ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer"},
        "matched_skills": {"type": "array", "items": {"type": "string"}},
        "missing_keywords": {"type": "array", "items": {"type": "string"}},
        "rewritten_bullets": {"type": "array", "items": {"type": "string"}},
        "ats_issues": {"type": "array", "items": {"type": "string"}},
        "justification": {"type": "string"},
    },
    "required": [
        "score",
        "matched_skills",
        "missing_keywords",
        "rewritten_bullets",
        "ats_issues",
        "justification",
    ],
}


def _api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise GeminiAPIError("GEMINI_API_KEY is not configured on the backend.")
    return api_key


def _generate(text: str, *, structured: bool = False) -> str:
    model = os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip()
    body: dict[str, Any] = {"contents": [{"parts": [{"text": text}]}]}
    if structured:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": ANALYSIS_SCHEMA,
            "temperature": 0.2,
            "maxOutputTokens": 1200,
        }

    try:
        response = HTTP_SESSION.post(
            GEMINI_API_URL.format(model=model),
            headers={"Content-Type": "application/json", "x-goog-api-key": _api_key()},
            json=body,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except requests.Timeout as exc:
        raise GeminiAPIError("Gemini timed out. Please try again.") from exc
    except requests.RequestException as exc:
        detail = ""
        if exc.response is not None:
            try:
                detail = exc.response.json().get("error", {}).get("message", "")
            except (ValueError, AttributeError):
                pass
        message = f"Gemini request failed: {detail or str(exc)}"
        raise GeminiAPIError(message) from exc
    except ValueError as exc:
        raise GeminiAPIError("Gemini returned a non-JSON HTTP response.") from exc

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        block_reason = data.get("promptFeedback", {}).get("blockReason")
        message = f"Gemini did not return content{f' ({block_reason})' if block_reason else ''}."
        raise GeminiAPIError(message) from exc


def call_gemini(prompt: str) -> dict:
    text = _generate(prompt, structured=True)
    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise GeminiAPIError("Gemini returned invalid analysis JSON.") from exc

    if not isinstance(result, dict):
        raise GeminiAPIError("Gemini returned an unexpected analysis format.")

    required = {
        "score",
        "matched_skills",
        "missing_keywords",
        "rewritten_bullets",
        "ats_issues",
        "justification",
    }
    if not required.issubset(result):
        raise GeminiAPIError("Gemini analysis is missing required fields.")

    list_fields = required - {"score", "justification"}
    if any(not isinstance(result[field], list) for field in list_fields):
        raise GeminiAPIError("Gemini returned an invalid analysis list.")

    try:
        result["score"] = max(0, min(100, int(result["score"])))
    except (TypeError, ValueError) as exc:
        raise GeminiAPIError("Gemini returned an invalid score.") from exc
    return result
