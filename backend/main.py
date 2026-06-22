from fastapi import FastAPI
from routes.match import router 

app = FastAPI(
    title="AI Resume Matcher",
    version="1.0.0"
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
