import os

import pytest

# Set fake keys before the app is imported; env vars take precedence over .env in pydantic-settings
os.environ.setdefault("NEWS_API_KEY", "test-news-key")
os.environ.setdefault("GROQ_API_KEY", "test-groq-key")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173")

# Clear any cached settings so the values above are used
from config import get_settings  # noqa: E402
get_settings.cache_clear()

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
