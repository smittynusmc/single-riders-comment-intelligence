from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.classification import CommentClassification
from app.models.comment import RawComment
from app.models.enums import PrimaryCategory
from app.models.signal import MvpSignal
from app.repositories.signals import SignalRepository
from app.schemas.dashboard import BreakdownItem, DashboardSummary, TopSignalSummary, TrendPoint


def ensure_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


class DashboardService:
    """Builds dashboard-friendly summary views from core tables."""

    def __init__(self, session: Session, signal_repository: SignalRepository):
        self.session = session
        self.signal_repository = signal_repository

    def get_summary(self) -> DashboardSummary:
        raw_comments = list(self.session.scalars(select(RawComment)))
        classifications = list(self.session.scalars(select(CommentClassification)))
        signals = list(self.session.scalars(select(MvpSignal)))
        week_start = datetime.now(UTC) - timedelta(days=7)

        total_comments = len(raw_comments)
        comments_this_week = sum(
            1
            for comment in raw_comments
            if ensure_utc(comment.comment_created_at or comment.created_at) >= week_start
        )
        needs_review_count = sum(1 for item in classifications if item.needs_human_review and not item.is_false_positive)

        category_counts = Counter((item.override_primary_category or item.primary_category).value for item in classifications)
        mvp_counts = Counter((item.override_mvp_area or item.mvp_area).value for item in classifications)
        top_repeated_requests = [
            BreakdownItem(key=signal.title, count=signal.evidence_count)
            for signal in sorted(signals, key=lambda item: item.evidence_count, reverse=True)[:5]
        ]
        safety_counts = Counter(
            (item.override_primary_category or item.primary_category).value
            for item in classifications
            if (item.override_primary_category or item.primary_category) in {PrimaryCategory.SAFETY_OR_TRUST, PrimaryCategory.MODERATION_OR_BOT}
        )

        return DashboardSummary(
            total_comments=total_comments,
            comments_this_week=comments_this_week,
            needs_review_count=needs_review_count,
            total_signals=len(signals),
            top_categories=[BreakdownItem(key=key, count=count) for key, count in category_counts.most_common(5)],
            top_mvp_areas=[BreakdownItem(key=key, count=count) for key, count in mvp_counts.most_common(5)],
            top_repeated_requests=top_repeated_requests,
            top_safety_concerns=[BreakdownItem(key=key, count=count) for key, count in safety_counts.most_common(5)],
        )

    def get_trends(self, days: int = 14) -> list[TrendPoint]:
        raw_comments = list(self.session.scalars(select(RawComment)))
        classifications = list(self.session.scalars(select(CommentClassification)))
        review_by_day = defaultdict(int)
        comment_by_day = defaultdict(int)
        start = datetime.now(UTC) - timedelta(days=days - 1)

        for comment in raw_comments:
            observed_at = ensure_utc(comment.comment_created_at or comment.created_at)
            if observed_at >= start:
                comment_by_day[observed_at.date().isoformat()] += 1

        for classification in classifications:
            if classification.needs_human_review and not classification.is_false_positive:
                observed_at = ensure_utc(classification.created_at)
                if observed_at >= start:
                    review_by_day[observed_at.date().isoformat()] += 1

        points: list[TrendPoint] = []
        for index in range(days):
            bucket = (start + timedelta(days=index)).date().isoformat()
            points.append(
                TrendPoint(
                    bucket=bucket,
                    comments=comment_by_day[bucket],
                    review_queue=review_by_day[bucket],
                )
            )
        return points

    def get_top_signals(self, limit: int = 5) -> list[TopSignalSummary]:
        return [
            TopSignalSummary(
                id=str(signal.id),
                title=signal.title,
                mvp_area=signal.mvp_area.value,
                evidence_count=signal.evidence_count,
                priority_score=signal.priority_score,
            )
            for signal in self.signal_repository.top(limit)
        ]
