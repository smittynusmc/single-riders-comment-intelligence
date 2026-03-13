from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base schema configured for ORM serialization."""

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class PaginationMeta(BaseModel):
    total: int
    limit: int
    offset: int


class PaginatedResponse(ORMModel, Generic[T]):
    items: list[T]
    meta: PaginationMeta


class TimestampMixin(ORMModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
