# Company News Briefing Tool — Project Spec

## What it does

A partner enters a company name, the app fetches recent news about that company, and an LLM turns those articles into a structured briefing they can use before a client meeting.

---

## Stack

- **Backend:** Python / FastAPI
- **Frontend:** React (Vite)
- **News data:** NewsAPI (free tier)
- **LLM:** Groq API (free tier — llama3-8b-8192, fast inference, no payment required)
- **Containerization:** Docker + docker-compose
- **Deployment:** EC2 t2.micro (backend), S3 + CloudFront (frontend)

---

## Backend

Entry point is `backend/main.py`. Keep business logic out of main — use a services layer.

### Structure
```
backend/
  main.py
  routers/
    brief.py
  services/
    news.py
    llm.py
    prompt.py
  models/
    brief.py
  requirements.txt
  Dockerfile
  .env
```

### Endpoints

**`POST /api/brief`**
- Takes `{ "company": "string" }`
- Fetches top 10 recent English articles from NewsAPI (last 30 days, sorted by date)
- Builds a prompt with those articles and calls Claude
- Returns structured JSON briefing

**`GET /health`**
- Returns `{ "status": "ok" }` for health checks

### LLM Prompt

Ask Groq (llama3-8b-8192) to act as a strategic analyst and return JSON only — no preamble. Response shape:

```json
{
  "summary": "2-3 sentences on what is happening with this company",
  "key_themes": ["theme 1", "theme 2", "theme 3"],
  "risks": ["risk 1", "risk 2"],
  "opportunities": ["opportunity 1", "opportunity 2"],
  "talking_points": ["point 1", "point 2", "point 3"]
}
```

### Error Handling

- 0 articles returned → `400` `"No recent news found for this company"`
- LLM failure → `500` `"Failed to generate briefing"`
- All errors returned as `{ "error": "message" }`

### Environment Variables
```
NEWS_API_KEY=
GROQ_API_KEY=
CORS_ORIGINS=http://localhost:5173,https://your-frontend-url
```

### Dependencies
```
fastapi
uvicorn
httpx
groq
python-dotenv
pydantic
```

---

## Frontend

Vite + React, minimal styling. Plain CSS or Tailwind — keep it clean.

### Structure
```
frontend/
  src/
    App.jsx
    components/
      SearchBar.jsx
      BriefingCard.jsx
      LoadingSpinner.jsx
      ErrorMessage.jsx
    services/
      api.js
  .env
  package.json
  Dockerfile
```

### Layout

Single page:
- Text input + submit button at the top
- Loading state while waiting for API response
- On success: company name, timestamp, then five sections — Summary, Key Themes, Risks, Opportunities, Talking Points
- On error: inline message below the search bar
- Use Bain red `#CC0000` as the accent colour

### API Call
```javascript
const response = await fetch(`${import.meta.env.VITE_API_URL}/api/brief`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ company: companyName })
});
```

### Environment Variables
```
VITE_API_URL=http://localhost:8000
```

---

## Docker

`docker-compose.yml` at the root — spins up both services together for local dev.

### docker-compose.yml
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    env_file:
      - ./frontend/.env
    depends_on:
      - backend
```

### Backend Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json .
RUN npm install
COPY . .
CMD ["npm", "run", "dev", "--", "--host"]
```

---

## Deployment (AWS Free Tier)

- **Backend:** EC2 t2.micro — SSH in, install Docker, run the backend container
- **Frontend:** Build the React app (`npm run build`), upload `dist/` to S3, serve via CloudFront

Set environment variables directly on EC2 — don't commit `.env` to the repo. Add `.env` to `.gitignore`.

---

## Repository Structure
```
/
  backend/
  frontend/
  docker-compose.yml
  README.md
```

---

## README Should Cover

- What the app does (2-3 sentences)
- How to run locally with Docker (`docker-compose up`)
- How to run without Docker (backend and frontend separately)
- What environment variables are needed and where to get them
- Live URL once deployed

---

## Code Quality

- Services are separate from routes — no business logic in `main.py`
- Pydantic models for all request/response shapes
- No hardcoded API keys anywhere in the codebase
- Frontend handles loading, error, and success states cleanly
- Works end to end with `docker-compose up` given valid API keys
