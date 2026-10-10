from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.ai.exceptions import AIServiceError
from app.api import auth, tasks

app = FastAPI(title="AI-Powered Task Management System", version="1.0.0")

app.include_router(auth.router)
app.include_router(tasks.router)


@app.exception_handler(AIServiceError)
def handle_ai_error(request: Request, exc: AIServiceError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}