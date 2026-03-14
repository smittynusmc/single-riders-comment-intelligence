from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.models.enums import MvpArea, PrimaryCategory


class BreakdownItem(BaseModel):
    key: str
    count: int


class VideoInsightItem(BaseModel):
    key: str
    label: str
    comment_count: int
    average_priority_score: float
    top_theme: str | None = None


class AudienceThemeInsight(BaseModel):
    key: str
    label: str
    summary: str
    story_anchor: str
    evidence_count: int
    weighted_score: float
    recent_evidence_count: int
    momentum: float
    trend_label: str
    mvp_area: MvpArea | None = None
    primary_category: PrimaryCategory | None = None
    sample_comments: list[str]


class AudienceInsightsResponse(BaseModel):
    mvp_priorities: list[AudienceThemeInsight]
    user_concerns: list[AudienceThemeInsight]
    confusion_points: list[AudienceThemeInsight]
    positive_validation: list[AudienceThemeInsight]
    story_alignment: list[AudienceThemeInsight]
    top_videos: list[VideoInsightItem]


class TrendPoint(BaseModel):
    bucket: str
    comments: int
    review_queue: int


class DashboardSummary(BaseModel):
    total_comments: int
    comments_this_week: int
    needs_review_count: int
    total_signals: int
    earliest_comment_date: datetime | None = None
    latest_comment_date: datetime | None = None
    months_represented: int = 0
    top_categories: list[BreakdownItem]
    top_mvp_areas: list[BreakdownItem]
    top_repeated_requests: list[BreakdownItem]
    top_safety_concerns: list[BreakdownItem]
    top_user_concerns: list[BreakdownItem]
    top_confusion_points: list[BreakdownItem]
    top_positive_validation: list[BreakdownItem]


class TopSignalSummary(BaseModel):
    id: str
    title: str
    mvp_area: str
    evidence_count: int
    priority_score: float
