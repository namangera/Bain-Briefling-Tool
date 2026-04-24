import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from logger import get_logger
from routers.brief import router as brief_router

log = get_logger("main")
log.info("Starting Bain Briefing API | log_level=%s", os.getenv("LOG_LEVEL", "INFO").upper())

app = FastAPI(title="Company News Briefing API")

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brief_router, prefix="/api")
