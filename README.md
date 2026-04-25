# Bain Company News Briefing Tool

A partner enters a company name and the app fetches the 10 most recent English news articles from the past 30 days, then uses Groq (llama-3.1-8b-instant) to synthesize a structured briefing. The output covers a summary, key themes, risks, opportunities, and talking points.

## Run locally with Docker

**Prerequisites:** Docker + Docker Compose, valid API keys (see below).

```bash
# Copy and fill in environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start both services
docker-compose up --build
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Health check: http://localhost:8000/api/health

## Testing

Backend tests run automatically during `docker build` — the image will not be created if any test fails.

To run tests locally without Docker:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m pytest tests/ -v
```

Tests use `unittest.mock` to stub out all NewsAPI and Groq calls — no real API keys are needed.

The suite covers: health check, correct response shape, no-news 400, and company name validation (empty, whitespace-only, too long, special-character stripping).

## Run without Docker

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in keys
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env   # set VITE_API_URL if needed
npm run dev
```

## Environment variables

### `backend/.env`

| Variable | Description | Where to get it |
|---|---|---|
| `NEWS_API_KEY` | NewsAPI key for fetching articles | [newsapi.org](https://newsapi.org) — free tier |
| `GROQ_API_KEY` | Groq API key for LLM inference | [console.groq.com](https://console.groq.com) — free tier |
| `CORS_ORIGINS` | Comma-separated list of allowed frontend origins | e.g. `http://localhost:5173,https://your-frontend.com` |
| `LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | Default: `INFO`. Override at runtime: `LOG_LEVEL=DEBUG docker-compose up` |

### `frontend/.env`

| Variable | Description |
|---|---|
| `VITE_API_URL` | Base URL of the backend API (default: `http://localhost:8000`) |

## Live URL

[https://bain-briefling-tool-1.onrender.com](https://bain-briefling-tool-1.onrender.com)

 The live demo is hosted on Render's free tier, so the service may spin down after inactivity. The first request can take up to 60 seconds to cold-start.

