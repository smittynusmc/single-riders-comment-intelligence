from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.classification import CommentClassification
from app.models.comment import RawComment
from app.models.enums import PrimaryCategory
from app.models.signal import MvpSignal
from app.repositories.signals import SignalRepository
from app.schemas.dashboard import AudienceInsightsResponse, BreakdownItem, DashboardSummary, TopSignalSummary, TrendPoint
from app.services.audience_insights import AudienceInsightsService


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
        insights = AudienceInsightsService(self.session).get_insights()
        week_start = datetime.now(UTC) - timedelta(days=7)
        earliest_comment_date, latest_comment_date, months_represented = self._date_coverage(raw_comments)

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
            earliest_comment_date=earliest_comment_date,
            latest_comment_date=latest_comment_date,
            months_represented=months_represented,
            top_categories=[BreakdownItem(key=key, count=count) for key, count in category_counts.most_common(5)],
            top_mvp_areas=[BreakdownItem(key=key, count=count) for key, count in mvp_counts.most_common(5)],
            top_repeated_requests=top_repeated_requests,
            top_safety_concerns=[BreakdownItem(key=key, count=count) for key, count in safety_counts.most_common(5)],
            top_user_concerns=[BreakdownItem(key=item.label, count=item.evidence_count) for item in insights.user_concerns],
            top_confusion_points=[BreakdownItem(key=item.label, count=item.evidence_count) for item in insights.confusion_points],
            top_positive_validation=[BreakdownItem(key=item.label, count=item.evidence_count) for item in insights.positive_validation],
        )

    def get_trends(self) -> list[TrendPoint]:
        raw_comments = list(self.session.scalars(select(RawComment)))
        classifications = list(
            self.session.scalars(select(CommentClassification).options(selectinload(CommentClassification.normalized_comment)))
        )
        review_by_day = defaultdict(int)
        comment_by_day = defaultdict(int)
        comment_dates = [ensure_utc(comment.comment_created_at or comment.created_at) for comment in raw_comments]
        if not comment_dates:
            return []

        start = min(comment_dates)
        end = max(comment_dates)
        use_month_buckets = (end.date() - start.date()).days > 62

        for comment in raw_comments:
            observed_at = ensure_utc(comment.comment_created_at or comment.created_at)
            comment_by_day[self._trend_bucket(observed_at, use_month_buckets=use_month_buckets)] += 1

        for classification in classifications:
            if classification.needs_human_review and not classification.is_false_positive and classification.normalized_comment:
                observed_at = ensure_utc(
                    classification.normalized_comment.comment_created_at
                    or classification.normalized_comment.created_at
                    or classification.created_at
                )
                review_by_day[self._trend_bucket(observed_at, use_month_buckets=use_month_buckets)] += 1

        points: list[TrendPoint] = []
        for bucket in self._trend_buckets_between(start=start, end=end, use_month_buckets=use_month_buckets):
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

    def get_audience_insights(self, *, limit: int = 6) -> AudienceInsightsResponse:
        return AudienceInsightsService(self.session).get_insights(limit=limit)

    def _date_coverage(self, raw_comments: list[RawComment]) -> tuple[datetime | None, datetime | None, int]:
        dates = [ensure_utc(comment.comment_created_at or comment.created_at) for comment in raw_comments]
        if not dates:
            return None, None, 0

        earliest = min(dates)
        latest = max(dates)
        months_represented = len({(value.year, value.month) for value in dates})
        return earliest, latest, months_represented

    def _trend_bucket(self, observed_at: datetime, *, use_month_buckets: bool) -> str:
        if use_month_buckets:
            return observed_at.strftime("%Y-%m")
        return observed_at.date().isoformat()

    def _trend_buckets_between(self, *, start: datetime, end: datetime, use_month_buckets: bool) -> list[str]:
        if use_month_buckets:
            buckets: list[str] = []
            year = start.year
            month = start.month
            while (year, month) <= (end.year, end.month):
                buckets.append(f"{year:04d}-{month:02d}")
                month += 1
                if month > 12:
                    month = 1
                    year += 1
            return buckets

        total_days = (end.date() - start.date()).days + 1
        return [(start + timedelta(days=index)).date().isoformat() for index in range(total_days)]
