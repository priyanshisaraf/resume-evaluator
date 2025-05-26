from fastapi import FastAPI
from routes import match

app = FastAPI(title="AI Resume Matcher")

app.include_router(match.router)
