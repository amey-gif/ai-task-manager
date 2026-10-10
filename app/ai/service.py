import json

from pydantic import ValidationError

from app.ai.client import ask_ai
from app.ai.exceptions import AIServiceError
from app.schemas.ai import AIDescription, AISummary


def generate_description(title: str) -> str:
    prompt = (
        "You are a helpful project assistant. "
        f"Write a clear task description (2 to 3 sentences) for a task titled: {title}\n"
        'Reply only with JSON in this format: {"description": "..."}'
    )
    return _read_json(ask_ai(prompt), AIDescription).description


def summarize_task(title: str, description: str | None) -> str:
    prompt = (
        "You are a helpful project assistant. "
        "Summarize this task in one short sentence.\n"
        f"Title: {title}\n"
        f"Description: {description or 'No description provided'}\n"
        'Reply only with JSON in this format: {"summary": "..."}'
    )
    return _read_json(ask_ai(prompt), AISummary).summary


def _read_json(text: str, model):
    # Convert the AI text to JSON, then check it matches the expected shape
    try:
        data = json.loads(text)
        return model(**data)
    except (ValueError, TypeError, ValidationError):
        raise AIServiceError("The AI returned an invalid response.", 502)