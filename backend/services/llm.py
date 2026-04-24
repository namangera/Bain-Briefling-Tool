import json
import os

from groq import AsyncGroq

from logger import get_logger

log = get_logger(__name__)


async def generate_briefing(prompt: str) -> dict:
    client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

    log.info("Sending prompt to Groq | model=llama-3.1-8b-instant prompt_chars=%d", len(prompt))

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        content = response.choices[0].message.content.strip()
        log.debug("Groq raw response | chars=%d", len(content))

        result = json.loads(content)
        log.info("Briefing generated successfully")
        return result
    except json.JSONDecodeError as exc:
        log.error("Failed to parse Groq response as JSON | error=%s", exc)
        raise RuntimeError("Failed to generate briefing") from exc
    except Exception as exc:
        log.error("Groq API call failed | error=%s", exc)
        raise RuntimeError("Failed to generate briefing") from exc
