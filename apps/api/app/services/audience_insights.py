from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.classification import CommentClassification
from app.models.comment import RawComment
from app.models.enums import MvpArea, PrimaryCategory, SentimentLabel
from app.schemas.dashboard import AudienceInsightsResponse, AudienceThemeInsight, VideoInsightItem

RECENT_LOOKBACK_DAYS = 14


@dataclass(frozen=True, slots=True)
class AudienceThemeDefinition:
    key: str
    label: str
    summary: str
    story_anchor: str
    terms: tuple[str, ...] = ()
    mvp_areas: tuple[MvpArea, ...] = ()
    primary_categories: tuple[PrimaryCategory, ...] = ()
    sentiment_targets: tuple[SentimentLabel, ...] = ()


THEME_DEFINITIONS: tuple[AudienceThemeDefinition, ...] = (
    AudienceThemeDefinition(
        key="dating_mode",
        label="Dating Mode Demand",
        summary="Users want the app to support romantic intent clearly and confidently.",
        story_anchor="Supports the MVP story about choosing dating mode and finding relationship-oriented matches.",
        terms=("dating", "date", "dates", "relationship", "romantic", "single"),
        mvp_areas=(MvpArea.MATCHING,),
    ),
    AudienceThemeDefinition(
        key="friendship_mode",
        label="Friendship Mode Demand",
        summary="Users want a clear friendship path for solo park trips and platonic connection.",
        story_anchor="Supports the user story about friendship mode and feeling more comfortable going to parks with others.",
        terms=("friend", "friends", "friendship", "solo", "community", "connected"),
        mvp_areas=(MvpArea.COMMUNITY, MvpArea.MEETUPS),
        primary_categories=(PrimaryCategory.SOCIAL_COORDINATION,),
    ),
    AudienceThemeDefinition(
        key="park_day_coordination",
        label="Park-Day Coordination",
        summary="Comments ask for same-day coordination, meetup planning, and park-specific matching support.",
        story_anchor="Supports the profile and matching stories around meetup planning and park calendar coordination.",
        terms=("same day", "meetup", "meetups", "calendar", "park day", "trip", "passholder", "annual pass"),
        mvp_areas=(MvpArea.MEETUPS, MvpArea.PASSHOLDERS),
        primary_categories=(PrimaryCategory.SOCIAL_COORDINATION,),
    ),
    AudienceThemeDefinition(
        key="matching_and_filters",
        label="Matching & Filters",
        summary="Users care about quality matching, swipe decisions, and filters that shape who they see.",
        story_anchor="Supports the matching and matching-preferences user stories for filters, swipe actions, and better fit.",
        terms=("match", "matching", "swipe", "filter", "filters", "preference", "preferences", "distance", "interests"),
        mvp_areas=(MvpArea.MATCHING,),
        primary_categories=(PrimaryCategory.FEATURE_REQUEST, PrimaryCategory.SOCIAL_COORDINATION),
    ),
    AudienceThemeDefinition(
        key="profiles_and_identity",
        label="Profiles & Self-Expression",
        summary="Users want richer profiles that show personality, favorites, and who they are.",
        story_anchor="Supports the profile creation stories around photos, bios, favorites, and preference signaling.",
        terms=("profile", "bio", "photo", "photos", "favorite", "favorites", "rides", "movies", "hobbies", "pets", "children"),
        mvp_areas=(MvpArea.PROFILES,),
        primary_categories=(PrimaryCategory.FEATURE_REQUEST,),
    ),
    AudienceThemeDefinition(
        key="messaging_and_chat",
        label="Messaging & Chat",
        summary="Users care about being able to message matches easily and safely.",
        story_anchor="Supports the messaging stories for match chat, thread management, and ongoing conversation.",
        terms=("message", "messages", "messaging", "chat", "dm", "conversation", "unmatch"),
        mvp_areas=(MvpArea.MESSAGING,),
    ),
    AudienceThemeDefinition(
        key="safety_and_moderation",
        label="Safety & Moderation",
        summary="Trust, reporting, bot prevention, and moderation safeguards remain a top launch concern.",
        story_anchor="Supports the moderation stories and the beta plan requirement for report-user and trust flows.",
        terms=("safe", "safety", "report", "reported", "fake", "bot", "bots", "moderation", "trust", "creepy", "verify", "verification"),
        mvp_areas=(MvpArea.SAFETY, MvpArea.MODERATION),
        primary_categories=(PrimaryCategory.SAFETY_OR_TRUST, PrimaryCategory.MODERATION_OR_BOT),
    ),
    AudienceThemeDefinition(
        key="beta_and_onboarding",
        label="Beta Access & Onboarding",
        summary="Users want a clear way to join beta, sign up, and understand how the app starts.",
        story_anchor="Supports the beta execution plan and onboarding story for explicit dating/friendship setup and launch readiness.",
        terms=("beta", "waitlist", "onboarding", "signup", "sign up", "login", "google", "phone", "account"),
        mvp_areas=(MvpArea.ONBOARDING,),
        primary_categories=(PrimaryCategory.CONFUSION_OR_ONBOARDING, PrimaryCategory.FEATURE_REQUEST),
    ),
    AudienceThemeDefinition(
        key="account_lifecycle",
        label="Account Trust & Lifecycle",
        summary="Users want confidence around account persistence, deletion, and protection of their information.",
        story_anchor="Supports the account creation, stay-logged-in, two-factor, and delete-account stories from the MVP docs.",
        terms=("delete account", "logged in", "stay logged in", "2fa", "two-factor", "delete my account", "protect", "protected"),
        mvp_areas=(MvpArea.ONBOARDING, MvpArea.SAFETY, MvpArea.OPERATIONS),
        primary_categories=(PrimaryCategory.SAFETY_OR_TRUST, PrimaryCategory.CONFUSION_OR_ONBOARDING),
    ),
    AudienceThemeDefinition(
        key="positive_validation",
        label="Positive Validation",
        summary="Audience comments signal belief that the product solves a real problem worth building.",
        story_anchor="Supports validation that the core dating and friendship concept resonates with theme park users.",
        terms=("love", "amazing", "great", "need this", "want this", "excited", "thank you"),
        primary_categories=(PrimaryCategory.PRAISE_OR_DELIGHT,),
        sentiment_targets=(SentimentLabel.POSITIVE, SentimentLabel.MIXED),
    ),
)

CONCERN_THEME_KEYS = {"safety_and_moderation", "account_lifecycle", "beta_and_onboarding", "matching_and_filters"}
CONFUSION_THEME_KEYS = {"beta_and_onboarding", "matching_and_filters", "account_lifecycle"}
VALIDATION_THEME_KEYS = {"positive_validation", "dating_mode", "friendship_mode", "park_day_coordination"}
STORY_ALIGNMENT_THEME_KEYS = {
    "dating_mode",
    "friendship_mode",
    "profiles_and_identity",
    "matching_and_filters",
    "messaging_and_chat",
    "safety_and_moderation",
    "beta_and_onboarding",
    "account_lifecycle",
}


def ensure_utc(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def comment_timestamp(item: CommentClassification) -> datetime:
    comment = item.normalized_comment
    return ensure_utc(comment.comment_created_at or comment.created_at or datetime.now(UTC))


class AudienceInsightsService:
    """Builds ranked MVP themes and supporting evidence for internal product decision-making."""

    def __init__(self, session: Session):
        self.session = session

    def get_insights(self, *, limit: int = 6) -> AudienceInsightsResponse:
        classifications = list(
            self.session.scalars(
                select(CommentClassification).options(selectinload(CommentClassification.normalized_comment))
            )
        )
        raw_comments = list(self.session.scalars(select(RawComment).where(RawComment.is_duplicate.is_(False))))
        theme_rankings, theme_matches = self._build_theme_rankings(classifications)

        return AudienceInsightsResponse(
            mvp_priorities=theme_rankings[:limit],
            user_concerns=self._filter_rankings(theme_rankings, keys=CONCERN_THEME_KEYS, limit=4),
            confusion_points=self._filter_rankings(
                theme_rankings,
                keys=CONFUSION_THEME_KEYS,
                limit=4,
                category=PrimaryCategory.CONFUSION_OR_ONBOARDING,
            ),
            positive_validation=self._filter_rankings(
                theme_rankings,
                keys=VALIDATION_THEME_KEYS,
                limit=4,
                sentiment=SentimentLabel.POSITIVE,
            ),
            story_alignment=self._filter_rankings(theme_rankings, keys=STORY_ALIGNMENT_THEME_KEYS, limit=8),
            top_videos=self._build_top_videos(raw_comments=raw_comments, theme_matches=theme_matches),
        )

    def _build_theme_rankings(
        self,
        classifications: list[CommentClassification],
    ) -> tuple[list[AudienceThemeInsight], dict[str, list[CommentClassification]]]:
        recent_cutoff = datetime.now(UTC) - timedelta(days=RECENT_LOOKBACK_DAYS)
        matches_by_theme: dict[str, list[CommentClassification]] = defaultdict(list)

        for item in classifications:
            if item.is_false_positive or not item.normalized_comment:
                continue

            for theme in THEME_DEFINITIONS:
                if self._match_score(item, theme) > 0:
                    matches_by_theme[theme.key].append(item)

        rankings: list[AudienceThemeInsight] = []
        for theme in THEME_DEFINITIONS:
            matches = matches_by_theme.get(theme.key, [])
            if not matches:
                continue

            recent_evidence = [item for item in matches if comment_timestamp(item) >= recent_cutoff]
            average_score = sum(self._priority_score(item) for item in matches) / len(matches)
            evidence_boost = min(1.28, 1 + ((len(matches) - 1) * 0.06))
            weighted_score = round(min(99.0, average_score * evidence_boost), 2)
            momentum = round((len(recent_evidence) / len(matches)) * 100, 2)
            trend_label = self._trend_label(recent_count=len(recent_evidence), total_count=len(matches))
            effective_mvp_area = Counter(self._effective_mvp_area(item) for item in matches if self._effective_mvp_area(item))
            effective_category = Counter(self._effective_category(item) for item in matches if self._effective_category(item))
            sample_comments = list(dict.fromkeys(item.normalized_comment.original_text for item in matches))[:3]

            rankings.append(
                AudienceThemeInsight(
                    key=theme.key,
                    label=theme.label,
                    summary=theme.summary,
                    story_anchor=theme.story_anchor,
                    evidence_count=len(matches),
                    weighted_score=weighted_score,
                    recent_evidence_count=len(recent_evidence),
                    momentum=momentum,
                    trend_label=trend_label,
                    mvp_area=effective_mvp_area.most_common(1)[0][0] if effective_mvp_area else None,
                    primary_category=effective_category.most_common(1)[0][0] if effective_category else None,
                    sample_comments=sample_comments,
                )
            )

        rankings.sort(key=lambda item: (-item.weighted_score, -item.evidence_count, item.label))
        return rankings, matches_by_theme

    def _build_top_videos(
        self,
        *,
        raw_comments: list[RawComment],
        theme_matches: dict[str, list[CommentClassification]],
    ) -> list[VideoInsightItem]:
        classification_by_comment_id: dict[str, CommentClassification] = {}
        theme_counts_by_comment_id: dict[str, Counter[str]] = defaultdict(Counter)

        for theme_key, matches in theme_matches.items():
            for item in matches:
                comment_id = item.normalized_comment.source_comment_id
                classification_by_comment_id[comment_id] = item
                theme_counts_by_comment_id[comment_id][theme_key] += 1

        grouped: dict[str, list[RawComment]] = defaultdict(list)
        for item in raw_comments:
            grouped[item.source_video_id or "no-video-id"].append(item)

        insights: list[VideoInsightItem] = []
        for key, comments in grouped.items():
            priority_scores = [
                self._priority_score(classification_by_comment_id[item.source_comment_id])
                for item in comments
                if item.source_comment_id in classification_by_comment_id
            ]
            theme_counter = Counter()
            for item in comments:
                theme_counter.update(theme_counts_by_comment_id.get(item.source_comment_id, Counter()))

            insights.append(
                VideoInsightItem(
                    key=key,
                    label=key if key != "no-video-id" else "No video id (portability export)",
                    comment_count=len(comments),
                    average_priority_score=round(sum(priority_scores) / len(priority_scores), 2) if priority_scores else 0.0,
                    top_theme=self._theme_label(theme_counter.most_common(1)[0][0]) if theme_counter else None,
                )
            )

        insights.sort(key=lambda item: (-item.comment_count, -item.average_priority_score, item.label))
        return insights[:5]

    def _filter_rankings(
        self,
        rankings: list[AudienceThemeInsight],
        *,
        keys: set[str],
        limit: int,
        category: PrimaryCategory | None = None,
        sentiment: SentimentLabel | None = None,
    ) -> list[AudienceThemeInsight]:
        filtered = [item for item in rankings if item.key in keys]
        if category is not None:
            filtered = [item for item in filtered if item.primary_category == category]
        if sentiment is not None:
            matching_theme_keys = {
                theme.key
                for theme in THEME_DEFINITIONS
                if sentiment in theme.sentiment_targets
            }
            filtered = [item for item in filtered if item.key in matching_theme_keys or item.primary_category == PrimaryCategory.PRAISE_OR_DELIGHT]
        return filtered[:limit]

    def _match_score(self, item: CommentClassification, theme: AudienceThemeDefinition) -> int:
        score = 0
        effective_area = self._effective_mvp_area(item)
        effective_category = self._effective_category(item)
        text_blob = " ".join(
            filter(
                None,
                [
                    item.normalized_comment.normalized_text,
                    item.normalized_comment.original_text.lower(),
                    " ".join(item.normalized_comment.rules_matched).lower(),
                    " ".join(item.secondary_categories).lower(),
                    item.recommended_action.lower(),
                ],
            )
        )

        if effective_area in theme.mvp_areas:
            score += 2
        if effective_category in theme.primary_categories:
            score += 2
        if theme.sentiment_targets and item.sentiment in theme.sentiment_targets:
            score += 1

        score += min(3, sum(1 for term in theme.terms if term in text_blob))
        return score

    def _priority_score(self, item: CommentClassification) -> float:
        base_score = (item.mvp_relevance_score * 0.45) + (item.urgency_score * 0.35) + (item.confidence * 0.2)
        category = self._effective_category(item)
        if category in {PrimaryCategory.SAFETY_OR_TRUST, PrimaryCategory.MODERATION_OR_BOT}:
            base_score += 0.12
        if category == PrimaryCategory.CONFUSION_OR_ONBOARDING:
            base_score += 0.08
        if comment_timestamp(item) >= datetime.now(UTC) - timedelta(days=RECENT_LOOKBACK_DAYS):
            base_score += 0.05
        return round(min(0.99, base_score) * 100, 2)

    def _trend_label(self, *, recent_count: int, total_count: int) -> str:
        if recent_count >= max(3, total_count // 2):
            return "Rising"
        if recent_count:
            return "Active"
        return "Established"

    def _effective_mvp_area(self, item: CommentClassification) -> MvpArea | None:
        return item.override_mvp_area or item.mvp_area

    def _effective_category(self, item: CommentClassification) -> PrimaryCategory | None:
        return item.override_primary_category or item.primary_category

    def _theme_label(self, key: str) -> str:
        for theme in THEME_DEFINITIONS:
            if theme.key == key:
                return theme.label
        return key.replace("_", " ").title()
