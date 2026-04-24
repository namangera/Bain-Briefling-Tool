from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from logger import get_logger
from routers.brief import router as brief_router

settings = get_settings()
log = get_logger("main")
log.info("Starting Bain Briefing API | log_level=%s", settings.LOG_LEVEL.upper())

app = FastAPI(title="Company News Briefing API")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    msg = errors[0]["msg"].removeprefix("Value error, ") if errors else "Validation error"
    return JSONResponse(status_code=400, content={"error": msg})


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brief_router, prefix="/api")
