import asyncio

import openai

from app.core.logging import error_logger
from app.core.config import settings


class AIService:
    def __init__(self) -> None:
        self.api_key = settings.OPENAI_API_KEY or ""
        self.model = settings.OPENAI_MODEL or "gpt-3.5-turbo"

    async def analyze_async(self, *, text: str) -> dict[str, str]:
        return await asyncio.to_thread(self.analyze, text=text)

    def analyze(self, *, text: str) -> dict[str, str]:
        if not self.api_key:
            error_logger.warning("OpenAI API key not configured; using fallback AI result")
            return {"sentiment": "unknown", "category": "Other"}

        try:
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You analyze customer messages. Return JSON with two keys: "
                            "sentiment (positive, neutral, negative) and category "
                            "(Question, Feedback, Commercial, Bug, Other)."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                temperature=0.2,
                max_tokens=80,
            )
            content = response.choices[0].message.content or ""
            parsed = self._parse_response(content)
            return parsed
        except Exception as exc:
            error_logger.exception("AI analysis failed: %s", exc)
            return {"sentiment": "unknown", "category": "Other"}

    def _parse_response(self, content: str) -> dict[str, str]:
        cleaned = content.strip()
        if cleaned.startswith("{"):
            try:
                import json

                payload = json.loads(cleaned)
                sentiment = str(payload.get("sentiment", "unknown")).strip().lower()
                category = str(payload.get("category", "Other")).strip()
                if sentiment not in {"positive", "neutral", "negative"}:
                    sentiment = "unknown"
                if category not in {"Question", "Feedback", "Commercial", "Bug", "Other"}:
                    category = "Other"
                return {"sentiment": sentiment, "category": category}
            except Exception:
                pass

        return {"sentiment": "unknown", "category": "Other"}

    def ping(self) -> bool:
        if not self.api_key:
            return False

        try:
            client = openai.OpenAI(api_key=self.api_key)
            client.models.list()
            return True
        except Exception as exc:
            error_logger.warning("AI ping failed: %s", exc)
            return False
