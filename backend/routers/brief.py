from fastapi import APIRouter
from fastapi.responses import JSONResponse

from logger import get_logger
from models.brief import ArticleSummary, BriefRequest, BriefResponse
from services.llm import generate_briefing
from services.news import fetch_articles
from services.prompt import build_prompt

router = APIRouter()
log = get_logger(__name__)


@router.get("/health")
async def health():
    log.debug("Health check")
    return {"status": "ok"}


@router.post("/brief", response_model=BriefResponse)
async def create_brief(request: BriefRequest):
    log.info(
        "Brief requested | company=%s sort_by=%s from=%s to=%s domains=%s",
        request.company, request.sort_by, request.from_date, request.to_date, request.domains,
    )

    try:
        articles = await fetch_articles(
            company=request.company,
            from_date=request.from_date,
            to_date=request.to_date,
            sort_by=request.sort_by,
            domains=request.domains,
        )
    except ValueError as exc:
        log.warning("No articles found | company=%s error=%s", request.company, exc)
        return JSONResponse(status_code=400, content={"error": str(exc)})

    prompt = build_prompt(request.company, articles)

    try:
        briefing = await generate_briefing(prompt)
    except RuntimeError as exc:
        log.error("LLM failure | company=%s error=%s", request.company, exc)
        return JSONResponse(status_code=500, content={"error": str(exc)})

    log.info("Brief complete | company=%s", request.company)
    return BriefResponse(
        **briefing,
        articles=[ArticleSummary(**a) for a in articles],
    )
