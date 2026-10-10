from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
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
    
@app.exception_handler(SQLAlchemyError)
def handle_database_error(request: Request, exc: SQLAlchemyError):
    return JSONResponse(status_code=500, content={"detail": "A database error occurred. Please try again later."})