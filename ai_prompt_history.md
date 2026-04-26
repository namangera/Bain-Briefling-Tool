# Chat Log — Bain Technical Assessment Build Session

---

## Turn 1

**User:** I wrote out a spec sheet for a new product, lets begin to plan out the implementation of this product. Suggest an implementation plan and I will interrogate your plan to refine it, ask me any questions about the spec too.

*(User had `spec.md` open in IDE)*

**Assistant (Plan Mode):**

Read `spec.md` — a Company News Briefing Tool with FastAPI backend, React/Vite frontend, NewsAPI for data, Groq (llama3-8b-8192) for LLM, Docker + docker-compose, EC2 + S3/CloudFront deployment.

Asked two clarifying questions:

1. The spec lists Groq in the stack but says "calls Claude" in the endpoint description — which LLM?
   - **Answer: Groq (Recommended)**

2. Styling: Plain CSS or Tailwind?
   - **Answer: Plain CSS**

Produced implementation plan covering:
- 13 steps from repo scaffolding through README
- Backend: `main.py`, `routers/brief.py`, `services/news.py`, `services/llm.py`, `services/prompt.py`, `models/brief.py`
- Frontend: `App.jsx`, `App.css`, four components, `api.js`
- Docker: `docker-compose.yml`, both Dockerfiles
- Key decisions: Groq not Claude, plain CSS, `httpx.AsyncClient`, `temperature=0.3`, `.env.example` committed / `.env` gitignored

---

## Turn 2

**User:** *(Approved plan — implementation begins)*

**Assistant:**

Built the entire project from scratch:

**Backend**
- `backend/main.py` — FastAPI app, CORS from env, router mount
- `backend/routers/brief.py` — `POST /api/brief`, `GET /health`
- `backend/services/news.py` — async NewsAPI fetch, 30-day window, raises `ValueError` on empty
- `backend/services/prompt.py` — formats articles, instructs LLM to return JSON only
- `backend/services/llm.py` — Groq async client (`llama3-8b-8192`), parses JSON, raises `RuntimeError` on failure
- `backend/models/brief.py` — `BriefRequest`, `BriefResponse`, `ErrorResponse`
- `backend/requirements.txt`, `backend/Dockerfile`, `backend/.env.example`

**Frontend**
- `frontend/src/App.jsx` — state machine: idle → loading → success/error
- `frontend/src/App.css` — plain CSS, Bain red `#CC0000`
- `frontend/src/components/SearchBar.jsx`
- `frontend/src/components/BriefingCard.jsx`
- `frontend/src/components/LoadingSpinner.jsx`
- `frontend/src/components/ErrorMessage.jsx`
- `frontend/src/services/api.js`
- `frontend/package.json`, `frontend/vite.config.js`, `frontend/index.html`, `frontend/Dockerfile`, `frontend/.env.example`

**Infrastructure**
- `docker-compose.yml`
- `README.md`
- `.gitignore`

---

## Turn 3

**User:** I made a fix to the model we are using in Groq (changed to `llama-3.1-8b-instant`), and fixed a port issue. The request is successful now. Now I want to add a section that shows the results for the NewsAPI call — headlines, date, and ability to click on the article.

**Assistant:**

Three-layer change:

- **`backend/models/brief.py`** — added `ArticleSummary` model (`title`, `url`, `publishedAt`, `description`) and `articles: list[ArticleSummary]` field on `BriefResponse`
- **`backend/routers/brief.py`** — router maps articles into `ArticleSummary` and includes them in the response
- **`frontend/src/components/BriefingCard.jsx`** — added `SourcesList` component; each article renders as a clickable link opening in a new tab, with the date formatted as "24 Apr 2025"
- **`frontend/src/App.css`** — added `.sources-list`, `.source-item`, `.source-link`, `.source-date` styles; headline turns Bain red on hover

---

## Turn 4

**User:** Let's add better logging to print to stdout and an ephemeral log file within the instance. Add logging levels to docker-compose as a trigger.

**Assistant:**

- **`backend/logger.py`** (new) — central logger factory; configures root logger once; two handlers: `StreamHandler(stdout)` + `FileHandler(/tmp/app.log)`; format: `timestamp | level | module | message`; level from `LOG_LEVEL` env var, default `INFO`
- **`backend/main.py`** — imports `get_logger`, logs startup + active log level
- **`backend/routers/brief.py`** — logs request in, articles found, brief complete, 400/500 errors
- **`backend/services/news.py`** — logs fetch start, article count, no-results warning; `DEBUG` level for raw `totalResults`
- **`backend/services/llm.py`** — logs prompt sent (char count), JSON parse error, API failure; split `except` blocks for `JSONDecodeError` vs generic `Exception`
- **`docker-compose.yml`** — added `environment: LOG_LEVEL: ${LOG_LEVEL:-INFO}`; override with `LOG_LEVEL=DEBUG docker-compose up`
- **`backend/.env.example`** — added `LOG_LEVEL=INFO`

---

## Turn 5

**User:** Let's expose the option to filter news using a "from" and "to" date option, sortBy (publishedAt, popularity, relevancy), and an option to search by domains. *(Provided full NewsAPI `/v2/everything` reference.)*

**Assistant:**

**Backend**
- **`backend/models/brief.py`** — `BriefRequest` gains `from_date`, `to_date`, `sort_by` (`Literal`, default `"publishedAt"`), `domains`
- **`backend/services/news.py`** — `fetch_articles` accepts all four params; `from` defaults to 30-day lookback; `to` and `domains` only sent when set; fixed `utcnow()` deprecation → `datetime.now(timezone.utc)`
- **`backend/routers/brief.py`** — passes all filter fields through from request to service

**Frontend**
- **`frontend/src/services/api.js`** — `generateBriefing(company, filters)` only serialises non-empty fields
- **`frontend/src/components/FilterPanel.jsx`** (new) — collapsible panel with From/To date pickers, Sort By dropdown, Domains text field; red dot on toggle when any filter is active; "Clear filters" resets to defaults
- **`frontend/src/App.jsx`** — `filters` state object passed to `FilterPanel` and `generateBriefing`
- **`frontend/src/App.css`** — filter panel, toggle, fields, clear button styles

---

## Turn 6

**User:** Set relevancy as the default sorting method.

**Assistant:**

Updated default in three places to stay in sync:
- `backend/models/brief.py` — `sort_by` default `"relevancy"`
- `frontend/src/App.jsx` — `DEFAULT_FILTERS.sortBy = "relevancy"`
- `frontend/src/components/FilterPanel.jsx` — `hasActiveFilters` check uses `"relevancy"` as baseline (so the red dot doesn't appear when relevancy is selected)

---

## Turn 7

**User:** The domain filtering is incorrect — it should match this format: `GET https://newsapi.org/v2/everything?domains=techcrunch.com,thenextweb.com&apiKey=`

**Assistant:**

`httpx` percent-encodes commas in the `params` dict (`%2C`), breaking the NewsAPI format. Fix: use `urllib.parse.urlencode` for all normal params, then append `&domains=...` as a raw string so commas are never encoded.

```python
query = urllib.parse.urlencode(params)
if domains:
    query += f"&domains={domains}"
url = f"{NEWS_API_URL}?{query}"
```

---

## Turn 8

**User:** *(Selected the domain→source ID map from a curl against the NewsAPI sources endpoint)*

The NewsAPI doesn't index some publications by URL — here is the domain→source ID mapping:
`bloomberg.com → bloomberg`, `wsj.com → the-wall-street-journal`, etc.

**Assistant:**

Added `DOMAIN_TO_SOURCE` dict and `_resolve_domains()` helper to `backend/services/news.py`:

- **Known domain** (e.g. `bloomberg.com`) → looked up → appended as `sources=bloomberg`
- **Unknown domain** (e.g. `ft.com`) → passed through as-is → appended as `domains=ft.com`
- Both can appear in the same request
- `www.` prefix stripped before lookup

---

## Turn 9

**User:** Let's make the "Restrict to Domains" section a dropdown where the user can select domains from the approved list.

**Assistant:**

- **`frontend/src/constants/sources.js`** (new) — `APPROVED_SOURCES` array of `{ domain, label }` pairs mirroring the backend map
- **`frontend/src/components/FilterPanel.jsx`** — replaced text input with `SourceDropdown` component: checkbox list in a positioned menu, closes on click-outside via `useRef` + `useEffect`; toggle button shows "All sources" / single label / "N sources selected"; selected sources render as removable pills
- **`frontend/src/App.jsx`** — `domains` state changed from `string` to `string[]`
- **`frontend/src/services/api.js`** — joins array with `","` before sending
- **`frontend/src/App.css`** — dropdown toggle, scrollable menu, checkbox rows, Bain-red pills

---

## Turn 10

**User:** Let's make the "Restrict to Sources" option a search/autofill component to filter through the options.

**Assistant:**

Added search input pinned to top of dropdown, with scrollable options list below:

- `search` state inside `SourceDropdown`; auto-focuses on open, clears on close
- `filtered` list derived by matching `label` or `domain` against search term (case-insensitive)
- "No sources match '…'" empty state
- `source-search-wrapper` pinned above a `source-options-list` scroll container

---

## Turn 11

**User:** The NewsAPI is on the free plan and limits dates to 30 days back. Add a message if dates are set before 30 days and disable the Generate button when that's the case.

**Assistant:**

- **`frontend/src/App.jsx`** — `getDateError(filters)` computes cutoff (`today − 30 days`); returns error string if `fromDate` or `toDate` is before cutoff; passed as `dateError` prop to `FilterPanel`, folded into `disabled` on `SearchBar`
- **`frontend/src/components/FilterPanel.jsx`** — accepts `dateError` prop; renders red-tinted box between date row and sources dropdown when a date is out of range; only visible when filter panel is open
- **`frontend/src/components/SearchBar.jsx`** — now accepts explicit `disabled` prop; button disabled when `loading || !!dateError || !value.trim()`
- **`frontend/src/App.css`** — `.filter-date-error` style (red text, light red background, border)

---

## Turn 12

**User:** Let's implement a simple backend testing framework:
- Test `GET /health` returns 200
- Test `POST /api/brief` with a valid company name returns the right shape
- Test `POST /api/brief` with a company that returns no news gives a 400
- Mock the NewsAPI and Groq calls — no real API calls in tests

**Assistant:**

- **`backend/pytest.ini`** — `pythonpath = .`, `testpaths = tests`
- **`backend/tests/__init__.py`**
- **`backend/tests/conftest.py`** — sets fake env vars before importing the app; exposes `client` fixture via `TestClient`
- **`backend/tests/test_brief.py`** — 3 tests: health, correct shape (mocked `fetch_articles` + `generate_briefing`), no-news 400
- **`backend/requirements.txt`** — added `pytest`

All 3 passed in 0.02s.

---

## Turn 13

**User:** Run the tests while building the image in Docker, and document in the README.

**Assistant:**

- **`backend/Dockerfile`** — added `RUN python -m pytest tests/ -v` between `COPY . .` and `CMD`; a failing test now aborts the build
- **`README.md`** — added Testing section explaining tests run on `docker build`, and the manual `pytest` command for local runs

Verified with `docker build ./backend --no-cache` — all 3 tests passed inside the container.

---

## Turn 14

**User:** I want to make two improvements to the backend:

1. **Config using pydantic BaseSettings** — `backend/config.py` with `pydantic_settings.BaseSettings`, validates all env vars at startup, fails fast if missing, `lru_cache` on `get_settings()`; all files import from config instead of `os.environ`

2. **Input validation on `POST /api/brief`** — reject empty strings (400 "Company name cannot be empty"), strip whitespace, max 100 chars (400 "Company name too long"), strip special characters for prompt injection protection (allow only alphanumeric, spaces, hyphens, periods, ampersands); all via Pydantic validators on the request model

**Assistant:**

**`backend/config.py`** (new)
```python
class Settings(BaseSettings):
    NEWS_API_KEY: str
    GROQ_API_KEY: str
    CORS_ORIGINS: str = "http://localhost:5173"
    LOG_LEVEL: str = "INFO"
    # reads from .env automatically via SettingsConfigDict

@lru_cache
def get_settings() -> Settings: ...
```

**`backend/models/brief.py`** — `@field_validator("company", mode="before")`:
1. Strip whitespace
2. Empty → `ValueError("Company name cannot be empty")`
3. Length > 100 → `ValueError("Company name too long")`
4. `re.sub(r"[^a-zA-Z0-9 \-\.&]", "", v)` sanitisation

**`backend/main.py`** — removed `load_dotenv()`, added `RequestValidationError` handler that strips Pydantic's `"Value error, "` prefix and returns `400 {"error": "..."}` instead of 422

**`backend/logger.py`**, **`backend/services/news.py`**, **`backend/services/llm.py`** — all `os.environ` reads replaced with `get_settings().<FIELD>`

**`backend/tests/conftest.py`** — calls `get_settings.cache_clear()` after setting test env vars

**`backend/tests/test_brief.py`** — 4 new tests: empty, whitespace-only, too long, special-char stripping (7 total, all passing)

**`backend/requirements.txt`** — added `pydantic-settings`

---

## Turn 15

**User:** Is the README still updated after these changes?

**Assistant:**

Two updates needed:
- Added `LOG_LEVEL` row to the `backend/.env` table with Docker override example
- Expanded Testing section to list all 7 test cases by category

---

## Turn 16

**User:** Export this entire chat log as a markdown file, call it `ai_prompt_history.md`.

**Assistant:** *(This file)*
