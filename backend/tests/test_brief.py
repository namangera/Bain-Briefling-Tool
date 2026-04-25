from unittest.mock import AsyncMock, patch

MOCK_ARTICLES = [
    {
        "title": "Apple reports record quarterly earnings",
        "description": "Apple Inc. beat analyst expectations across all product lines.",
        "url": "https://example.com/apple-q4",
        "publishedAt": "2025-04-20T10:00:00Z",
    },
    {
        "title": "Apple Vision Pro sales exceed forecasts",
        "description": "The mixed-reality headset has seen stronger than expected adoption.",
        "url": "https://example.com/apple-vision",
        "publishedAt": "2025-04-18T08:30:00Z",
    },
]

MOCK_BRIEFING = {
    "summary": "Apple continues to outperform market expectations with record revenue.",
    "key_themes": ["Strong earnings", "AI integration", "Services growth"],
    "risks": ["Supply chain exposure", "Regulatory scrutiny in EU"],
    "opportunities": ["Generative AI features", "Expansion in India"],
    "talking_points": ["Record Q4 revenue", "Vision Pro momentum", "Developer ecosystem strength"],
}


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_brief_returns_correct_shape(client):
    with (
        patch("routers.brief.fetch_articles", new=AsyncMock(return_value=MOCK_ARTICLES)),
        patch("routers.brief.generate_briefing", new=AsyncMock(return_value=MOCK_BRIEFING)),
    ):
        response = client.post("/api/brief", json={"company": "Apple"})

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data["summary"], str)
    assert isinstance(data["key_themes"], list)
    assert isinstance(data["risks"], list)
    assert isinstance(data["opportunities"], list)
    assert isinstance(data["talking_points"], list)
    assert isinstance(data["articles"], list)

    article = data["articles"][0]
    assert "title" in article
    assert "url" in article
    assert "publishedAt" in article

    assert data["summary"] == MOCK_BRIEFING["summary"]
    assert data["key_themes"] == MOCK_BRIEFING["key_themes"]
    assert len(data["articles"]) == len(MOCK_ARTICLES)


def test_brief_no_news_returns_400(client):
    with patch(
        "routers.brief.fetch_articles",
        new=AsyncMock(side_effect=ValueError("No recent news found for 'Nortrel'")),
    ):
        response = client.post("/api/brief", json={"company": "Nortrel"})

    assert response.status_code == 400
    assert response.json() == {"error": "No recent news found for 'Nortrel'"}


def test_brief_empty_company_returns_400(client):
    response = client.post("/api/brief", json={"company": ""})
    assert response.status_code == 400
    assert response.json() == {"error": "Company name cannot be empty"}


def test_brief_whitespace_only_returns_400(client):
    response = client.post("/api/brief", json={"company": "   "})
    assert response.status_code == 400
    assert response.json() == {"error": "Company name cannot be empty"}


def test_brief_company_too_long_returns_400(client):
    response = client.post("/api/brief", json={"company": "A" * 101})
    assert response.status_code == 400
    assert response.json() == {"error": "Company name too long"}


def test_brief_strips_special_chars(client):
    with patch("routers.brief.fetch_articles", new=AsyncMock(return_value=MOCK_ARTICLES)) as mock_fetch:
        with patch("routers.brief.generate_briefing", new=AsyncMock(return_value=MOCK_BRIEFING)):
            response = client.post("/api/brief", json={"company": "Apple; DROP TABLE companies--"})

    assert response.status_code == 200
    called_with = mock_fetch.call_args.kwargs["company"]
    # Semicolons stripped; hyphens are allowed (e.g. Rolls-Royce)
    assert ";" not in called_with
    assert "Apple" in called_with
