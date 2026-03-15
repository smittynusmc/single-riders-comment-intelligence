from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PythonEnum
from typing import TypeVar

from sqlalchemy import DateTime, Enum as SqlEnum, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

EnumT = TypeVar("EnumT", bound=PythonEnum)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def value_enum(enum_cls: type[EnumT], *, name: str) -> SqlEnum:
    """Persist enum values so ORM labels match the PostgreSQL enum definitions."""

    return SqlEnum(
        enum_cls,
        name=name,
        values_callable=lambda members: [member.value for member in members],
        validate_strings=True,
    )


class TimestampedModel:
    """Reusable primary key and timestamp columns."""

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
