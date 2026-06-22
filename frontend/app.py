import os

import requests
import streamlit as st


def get_api_url() -> str:
    configured_url = os.getenv("API_URL")
    if configured_url:
        return configured_url.rstrip("/")
    try:
        configured_url = st.secrets.get("API_URL")
    except Exception:
        # Streamlit raises its own exception when no secrets file exists locally.
        configured_url = None
    return (configured_url or "http://localhost:8000").rstrip("/")


st.set_page_config(page_title="AI Resume Evaluator", layout="centered")
st.title("📄 AI Resume Evaluator + Job Matcher")

with st.expander("🔒 How your resume is handled"):
    st.write(
        "Your file is read in memory for this analysis and is not saved by this app. "
        "The extracted resume text and job description are sent to Google Gemini to "
        "produce the evaluation. Analysis responses are marked as non-cacheable. "
        "Avoid uploading information you do not want processed by the AI provider."
    )

resume_file = st.file_uploader("Upload your Resume (.pdf or .docx)", type=["pdf", "docx"])
job_description = st.text_area("Paste the Job Description here")

short_jd = bool(job_description and len(job_description.split()) < 20)
if short_jd:
    st.warning("⚠️ The job description seems short. A fuller description gives better results.")
    trigger_analysis = st.button("Analyze Anyway")
else:
    trigger_analysis = st.button("Analyze Resume")

if trigger_analysis and resume_file and job_description.strip():
    with st.spinner("Analyzing..."):
        try:
            response = requests.post(
                f"{get_api_url()}/analyze",
                files={
                    "resume": (
                        resume_file.name,
                        resume_file.getvalue(),
                        resume_file.type,
                    )
                },
                data={"job_description": job_description},
                timeout=120,
            )

            if response.ok:
                st.success("✅ Analysis Complete!")
                result = response.json()["result"]

                if result.get("used_typical_requirements", False):
                    st.info("ℹ️ Typical requirements for this role were used for the comparison.")

                st.subheader("📊 Match Score")
                st.progress(result["score"] / 100)
                st.write(f"Score: **{result['score']} / 100**")

                matched_column, missing_column = st.columns(2)
                with matched_column:
                    st.subheader("✅ Matched Skills")
                    if result["matched_skills"]:
                        for skill in result["matched_skills"]:
                            st.markdown(f"- {skill}")
                    else:
                        st.write("No clear matches detected.")

                with missing_column:
                    st.subheader("🔎 Missing Keywords")
                    if result["missing_keywords"]:
                        for keyword in result["missing_keywords"]:
                            st.markdown(f"- {keyword}")
                    else:
                        st.write("No important keywords missing.")

                st.subheader("✍️ Rewritten Resume Bullets")
                if result["rewritten_bullets"]:
                    for index, bullet in enumerate(result["rewritten_bullets"], 1):
                        st.markdown(f"**{index}.** {bullet}")
                else:
                    st.write("No bullet rewrites suggested.")

                st.subheader("🤖 ATS Formatting Issues")
                if result["ats_issues"]:
                    for issue in result["ats_issues"]:
                        st.warning(issue)
                else:
                    st.success("No obvious ATS issues found in the extracted text.")

                st.subheader("Why this score?")
                st.write(result.get("justification", "No explanation provided."))
            else:
                try:
                    detail = response.json().get("detail", response.text)
                except requests.JSONDecodeError:
                    detail = response.text
                st.error(f"Server error: {response.status_code}")
                st.code(detail)

        except requests.Timeout:
            st.error("❌ The analysis timed out. Please try again.")
        except requests.RequestException as exc:
            st.error("❌ Could not connect to the analysis server.")
            st.code(str(exc))
elif trigger_analysis:
    st.warning("Please upload a resume and enter a job description.")
