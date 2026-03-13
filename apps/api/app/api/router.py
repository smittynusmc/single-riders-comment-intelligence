from __future__ import annotations

from fastapi import APIRouter

from app.api.routes import classifications, comments, dashboard, imports, signals

api_router = APIRouter()
api_router.include_router(imports.router, tags=["imports"])
api_router.include_router(comments.router, tags=["comments"])
api_router.include_router(classifications.router, tags=["classifications"])
api_router.include_router(signals.router, tags=["signals"])
api_router.include_router(dashboard.router, tags=["dashboard"])
