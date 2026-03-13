from __future__ import annotations

from enum import Enum


class SourcePlatform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    DISCORD = "discord"
    APP_STORE = "app_store"
    MANUAL = "manual"
    GENERIC_SOCIAL = "generic_social"
    UNKNOWN = "unknown"


class IngestionSourceType(str, Enum):
    CSV = "csv"
    MANUAL_PASTE = "manual_paste"
    THIRD_PARTY_EXPORT = "third_party_export"
    CONNECTOR_PLACEHOLDER = "connector_placeholder"


class IngestionStatus(str, Enum):
    PENDING = "pending"
    IMPORTED = "imported"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class NormalizationStatus(str, Enum):
    PENDING = "pending"
    NORMALIZED = "normalized"
    SKIPPED_DUPLICATE = "skipped_duplicate"
    FAILED = "failed"


class ClassificationStatus(str, Enum):
    PENDING = "pending"
    CLASSIFIED = "classified"
    NEEDS_REVIEW = "needs_review"
    APPROVED = "approved"
    FALSE_POSITIVE = "false_positive"


class SignalStatus(str, Enum):
    ACTIVE = "active"
    REVIEWED = "reviewed"
    ARCHIVED = "archived"


class PrimaryCategory(str, Enum):
    FEATURE_REQUEST = "feature_request"
    BUG_OR_QUALITY = "bug_or_quality"
    SAFETY_OR_TRUST = "safety_or_trust"
    MODERATION_OR_BOT = "moderation_or_bot"
    SOCIAL_COORDINATION = "social_coordination"
    CONFUSION_OR_ONBOARDING = "confusion_or_onboarding"
    PRAISE_OR_DELIGHT = "praise_or_delight"
    PRICING_OR_VALUE = "pricing_or_value"
    OTHER = "other"


class MvpArea(str, Enum):
    MATCHING = "matching"
    MEETUPS = "meetups"
    SAFETY = "safety"
    ONBOARDING = "onboarding"
    PROFILES = "profiles"
    MODERATION = "moderation"
    MESSAGING = "messaging"
    MONETIZATION = "monetization"
    PASSHOLDERS = "passholders"
    COMMUNITY = "community"
    OPERATIONS = "operations"
    OTHER = "other"


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    MIXED = "mixed"
