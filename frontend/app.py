import streamlit as st
import requests

st.set_page_config(page_title="AI Resume Evaluator", layout="centered")

st.title("\U0001F4C4 AI Resume Evaluator + Job Matcher")

# File uploader
resume_file = st.file_uploader("Upload your Resume (.pdf or .docx)", type=["pdf", "docx"])

# Job description input
job_description = st.text_area("Paste the Job Description here")

# Check if job description is too short
short_jd = job_description and len(job_description.split()) < 20

# Show appropriate button depending on input
if short_jd:
    st.warning("⚠️ The job description seems very short. Please paste the full description for better results.")
    trigger_analysis = st.button("Analyze Anyway")
else:
    trigger_analysis = st.button("Analyze Resume")

# Only run if user clicks button and has uploaded a resume
if trigger_analysis and resume_file and job_description:

    with st.spinner("Sending to AI..."):
        try:
            # Prepare the request
            files = {"resume": resume_file.getvalue()}
            data = {"job_description": job_description}

            response = requests.post(
                "https://resume-evaluator-0mnn.onrender.com/analyze",
                files={"resume": (resume_file.name, resume_file, resume_file.type)},
                data=data
            )

            if response.status_code == 200:
                st.success("\u2705 Analysis Complete!")
                result = response.json()["result"]

                # Let user know if job description was generated
                if result.get("auto_generated", False):
                    st.info("\u2139\ufe0f The job description was auto-generated based on the job title you entered.")

                # Match Score
                st.subheader("\U0001F4CA Match Score")
                st.progress(result["score"] / 100)
                st.write(f"Score: **{result['score']} / 100**")

                # Missing Skills
                st.subheader("\U0001F9E9 Missing Skills")
                if result["missing_skills"]:
                    for skill in result["missing_skills"]:
                        st.markdown(f"- \u274C **{skill}**")
                    if result.get("auto_generated", False):
                        st.caption("\u2139\ufe0f Showing general missing skills based on job title.")
                else:
                    st.write("No major missing skills detected.")

                # Suggestions
                st.subheader("\u270D\ufe0f Improved Resume Bullet Points")
                if result["suggestions"]:
                    for i, bullet in enumerate(result["suggestions"], 1):
                        st.markdown(f"**{i}.** {bullet}")
                else:
                    st.write("No improvements suggested.")

                st.subheader("📄 AI-Generated Cover Letter")
                if result.get("cover_letter"):
                    st.text_area("Generated Cover Letter", result["cover_letter"], height=300)
                    st.download_button(
                        label="📥 Download Cover Letter (txt)",
                        data=result["cover_letter"],
                        file_name="cover_letter.txt",
                        mime="text/plain"
                    )
                else:
                    st.info("Cover letter not available.")

                # Justification
                st.subheader("Why this score\u2753")
                st.write(result.get("justification", "No explanation provided."))

            else:
                st.error(f"Server error: {response.status_code}")
                st.code(response.text)

        except Exception as e:
            st.error("\u274c Request failed")
            st.code(str(e))
