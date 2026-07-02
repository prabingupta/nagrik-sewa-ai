import json
import time

from google import genai
from google.genai import errors as genai_errors
from django.conf import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

SYSTEM_PROMPT = """You are Nagarik Sewa AI, an assistant that helps Nepali citizens \
understand government services (passport, citizenship certificate, driving license, etc.).

You must respond ONLY with valid JSON, no preamble, no markdown code fences, matching \
exactly this schema:

{
  "service_name": "string - name of the service being asked about",
  "steps": ["string", "..."],
  "documents": ["string", "..."],
  "cost": "string - estimated fee, or 'Not specified' if unknown",
  "office": "string - relevant government office or department",
  "tips": ["string", "..."]
}

Rules:
- Be accurate. If you are not fully certain about a specific fee or step, say so \
  clearly in that field rather than inventing precise numbers.
- Keep steps concise and in logical order.
- If the question is not about a Nepali government service, set "service_name" to \
  "Unknown" and explain in "tips" that you can only help with government service queries.
- Respond in the requested language (English or Nepali), including field values.
"""


def _fallback_answer(message: str) -> dict:
    return {
        "service_name": "Unknown",
        "steps": [],
        "documents": [],
        "cost": "Not specified",
        "office": "Not specified",
        "tips": [message],
    }


def get_service_guidance(question: str, language: str = "en") -> dict:
    """Calls Gemini to get structured guidance for a government service question."""
    lang_label = "Nepali" if language == "ne" else "English"

    user_message = (
        f"{SYSTEM_PROMPT}\n\n"
        f"User question: {question}\n"
        f"Respond in {lang_label}.\n"
        f"Remember: respond with JSON only, matching the schema exactly."
    )

    max_attempts = 3
    last_error = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=user_message,
            )
            raw_text = response.text.strip()

            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:].strip()

            return json.loads(raw_text)

        except genai_errors.ServerError as e:
            last_error = e
            if attempt < max_attempts:
                time.sleep(2 * attempt)  # simple backoff: 2s, 4s
                continue
        except json.JSONDecodeError:
            return _fallback_answer(
                "Sorry, something went wrong parsing the AI response. Please try again."
            )

    # All retries exhausted
    return _fallback_answer(
        "The AI service is temporarily busy (high demand on the free tier). "
        "Please try again in a moment."
    )
