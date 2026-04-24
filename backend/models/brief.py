from typing import Literal

from pydantic import BaseModel


class BriefRequest(BaseModel):
    company: str
    from_date: str | None = None
    to_date: str | None = None
    sort_by: Literal["publishedAt", "popularity", "relevancy"] = "relevancy"
    domains: str | None = None


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
