from fastapi import FastAPI

from app.api import auth, tasks

app = FastAPI(title="AI-Powered Task Management System", version="1.0.0")

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}