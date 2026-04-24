import os
import urllib.parse
from datetime import datetime, timedelta, timezone

import httpx

NEWS_API_URL = "https://newsapi.org/v2/everything"

DOMAIN_TO_SOURCE = {
    "abcnews.go.com": "abc-news",
    "abc.net.au": "abc-news-au",
    "aljazeera.com": "al-jazeera-english",
    "arstechnica.com": "ars-technica",
    "apnews.com": "associated-press",
    "afr.com": "australian-financial-review",
    "axios.com": "axios",
    "bbc.co.uk": "bbc-news",
    "bbc.com": "bbc-news",
    "bleacherreport.com": "bleacher-report",
    "bloomberg.com": "bloomberg",
    "breitbart.com": "breitbart-news",
    "businessinsider.com": "business-insider",
    "buzzfeed.com": "buzzfeed",
    "cbc.ca": "cbc-news",
    "cbsnews.com": "cbs-news",
    "cnn.com": "cnn",
    "engadget.com": "engadget",
    "financialpost.com": "financial-post",
    "fortune.com": "fortune",
    "foxnews.com": "fox-news",
    "independent.co.uk": "independent",
    "mashable.com": "mashable",
    "nbcnews.com": "nbc-news",
    "nationalgeographic.com": "national-geographic",
    "newsweek.com": "newsweek",
    "politico.com": "politico",
    "techcrunch.com": "techcrunch",
    "techradar.com": "techradar",
    "theglobeandmail.com": "the-globe-and-mail",
    "thehill.com": "the-hill",
    "theverge.com": "the-verge",
    "time.com": "time",
    "usatoday.com": "usa-today",
    "washingtonpost.com": "the-washington-post",
    "wired.com": "wired",
    "wsj.com": "the-wall-street-journal",
}


def _resolve_domains(raw: str) -> tuple[list[str], list[str]]:
    """Split user input into (source_ids, plain_domains) based on the known map."""
    source_ids, plain_domains = [], []
    for entry in raw.split(","):
        domain = entry.strip().lower().lstrip("www.")
        if not domain:
            continue
        if domain in DOMAIN_TO_SOURCE:
            source_ids.append(DOMAIN_TO_SOURCE[domain])
        else:
            plain_domains.append(domain)
    return source_ids, plain_domains


async def fetch_articles(
    company: str,
    from_date: str | None = None,
    to_date: str | None = None,
    sort_by: str = "relevancy",
    domains: str | None = None,
) -> list[dict]:
    api_key = os.environ["NEWS_API_KEY"]
    default_from = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")

    params = {
        "q": company,
        "language": "en",
        "sortBy": sort_by,
        "pageSize": 10,
        "from": from_date or default_from,
        "apiKey": api_key,
    }

    if to_date:
        params["to"] = to_date

    # Build the query string; domains/sources must not have commas percent-encoded
    raw_fragments = []
    if domains:
        source_ids, plain_domains = _resolve_domains(domains)
        if source_ids:
            raw_fragments.append(f"sources={','.join(source_ids)}")
        if plain_domains:
            raw_fragments.append(f"domains={','.join(plain_domains)}")

    query = urllib.parse.urlencode(params)
    if raw_fragments:
        query += "&" + "&".join(raw_fragments)

    url = f"{NEWS_API_URL}?{query}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    articles = data.get("articles", [])
    if not articles:
        raise ValueError(f"No recent news found for '{company}'")

    return [
        {
            "title": a.get("title") or "",
            "description": a.get("description") or "",
            "url": a.get("url") or "",
            "publishedAt": a.get("publishedAt") or "",
        }
        for a in articles
    ]
