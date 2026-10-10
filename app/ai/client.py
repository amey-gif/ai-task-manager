import httpx

from app.ai.exceptions import AIServiceError
from app.config import get_settings


def ask_ai(prompt: str) -> str:
    settings = get_settings()

    # 1. Make sure the key is configured
    if not settings.ai_api_key:
        raise AIServiceError("AI is not configured. Set AI_API_KEY in the .env file.", 503)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.ai_model}:generateContent"
    headers = {"x-goog-api-key": settings.ai_api_key}
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"},
    }

    # 2. Call the API and handle network problems
    try:
        response = httpx.post(url, headers=headers, json=body, timeout=settings.ai_timeout_seconds)
    except httpx.TimeoutException:
        raise AIServiceError("The AI service took too long to respond.", 504)
    except httpx.RequestError:
        raise AIServiceError("Could not reach the AI service.", 502)

    # 3. Handle error responses from the provider
    if response.status_code != 200:
        raise AIServiceError("The AI service returned an error.", 502)

    # 4. Pull the generated text out of the response
    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, ValueError):
        raise AIServiceError("The AI service returned an unexpected response.", 502)