# AI Resume Evaluator + Smart Job Matcher
An AI-powered web app that analyzes resumes, scores them against job descriptions, identifies missing skills and suggests improvements — all in one place.

## Demo
**Frontend:** [Streamlit App](https://resume-evaluator-cqwactuahpxxbz2owehkwe.streamlit.app/)  
**Backend API:** [Render Deployment](https://resume-evaluator-0mnn.onrender.com)

## Features

- Upload your resume (PDF or DOCX)
- Paste a job description or just a role title
- AI evaluates match score (0–100)
- Highlights missing skills
- Suggests resume bullet improvements

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** FastAPI
- **AI Model:** Gemini 1.5 Pro (Google Generative Language API)
- **Text Parsing:** PyMuPDF, python-docx
- **Hosting:** Render (API) + Streamlit Cloud (UI)
- **Language:** Python 3.10+

## Project Structure

```bash
resume-evaluator/
├── frontend/
│   ├── app.py                      # Streamlit app
│   ├── components/
│   │   └── upload_widget.py       # UI components
│   └── requirements.txt           # Frontend dependencies
│
├── backend/
│   ├── main.py                    # FastAPI entry point
│   ├── routes/
│   │   └── match.py               # API route for analysis
│   ├── utils/
│   │   ├── parser.py              # Resume file reader
│   │   └── prompts.py             # Prompt logic
│   └── requirements.txt           # Backend dependencies
└── README.md
```

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/priyanshisaraf/resume-evaluator.git
cd resume-evaluator
```

### 2. Backend Setup (FastAPI)
```bash
cd backend
cp .env.example .env           # Create and fill in your API key
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Frontend Setup (Streamlit)
```bash
cd ../frontend
pip install -r requirements.txt
streamlit run app.py
```

---

## Deployment

### Backend on Render
- Connect GitHub repo
- Root directory: `backend/`
- Start Command:
  ```bash
  uvicorn main:app --host=0.0.0.0 --port=10000
  ```
- Add environment variable: `GEMINI_API_KEY`

### Frontend on Streamlit Cloud
- Point to `frontend/app.py`
- Add secret via `secrets.toml` or Streamlit Cloud UI:
  ```toml
  GEMINI_API_KEY = "your-api-key"
  ```

---

## Environment Variables

| Key              | Description                     |
|------------------|---------------------------------|
| `GEMINI_API_KEY` | Required to access Gemini API   |

---

## Author

**Priyanshi Saraf**  
- [GitHub](https://github.com/priyanshisaraf) 
- [LinkedIn](https://www.linkedin.com/in/priyanshisaraf)

---

## License

This project is not currently licensed. If you'd like to contribute, reuse, or adapt this work, please contact the author for permissions or collaboration inquiries.

