from __future__ import annotations

from pydantic import BaseModel


class BreakdownItem(BaseModel):
    key: str
    count: int


class TrendPoint(BaseModel):
    bucket: str
    comments: int
    review_queue: int


class DashboardSummary(BaseModel):
    total_comments: int
    comments_this_week: int
    needs_review_count: int
    total_signals: int
    top_categories: list[BreakdownItem]
    top_mvp_areas: list[BreakdownItem]
    top_repeated_requests: list[BreakdownItem]
    top_safety_concerns: list[BreakdownItem]


class TopSignalSummary(BaseModel):
    id: str
    title: str
    mvp_area: str
    evidence_count: int
    priority_score: float
