def build_prompt(company: str, articles: list[dict]) -> str:
    formatted = "\n".join(
        f"[{i + 1}] Title: {a['title']} | Description: {a['description']}"
        for i, a in enumerate(articles)
    )

    return f"""You are a strategic analyst preparing a partner at a management consulting firm for a client meeting.

Based on the following recent news articles about {company}, return a JSON object with EXACTLY this shape and NO other text:

{{
  "summary": "2-3 sentences on what is happening with this company, place more weight on recent developments and fundamental changes rather than minor news",
  "key_themes": ["theme 1", "theme 2", "theme 3"],
  "risks": ["risk 1", "risk 2"],
  "opportunities": ["opportunity 1", "opportunity 2"],
  "talking_points": ["point 1", "point 2", "point 3"]
}}

NEWS ARTICLES:
{formatted}

Return valid JSON only. No preamble, no explanation, no markdown fences."""
