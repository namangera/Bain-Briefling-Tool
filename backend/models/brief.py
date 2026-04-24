import re
from typing import Literal

from pydantic import BaseModel, field_validator


class BriefRequest(BaseModel):
    company: str
    from_date: str | None = None
    to_date: str | None = None
    sort_by: Literal["publishedAt", "popularity", "relevancy"] = "relevancy"
    domains: str | None = None

    @field_validator("company", mode="before")
    @classmethod
    def validate_company(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Company name cannot be empty")
        if len(v) > 100:
            raise ValueError("Company name too long")
        v = re.sub(r"[^a-zA-Z0-9 \-\.&]", "", v)
        if not v:
            raise ValueError("Company name cannot be empty")
        return v


class ArticleSummary(BaseModel):
    title: str
    description: str
    url: str
    publishedAt: str


class BriefResponse(BaseModel):
    summary: str
    key_themes: list[str]
    risks: list[str]
    opportunities: list[str]
    talking_points: list[str]
    articles: list[ArticleSummary]


class ErrorResponse(BaseModel):
    error: str
