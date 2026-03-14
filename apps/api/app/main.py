from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Internal product intelligence API for social comments and MVP signals.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def require_internal_api_token(request: Request, call_next):
    if request.url.path == "/health" or not settings.internal_api_token:
        return await call_next(request)

    if request.headers.get("x-internal-api-token") != settings.internal_api_token:
        return JSONResponse(status_code=401, content={"detail": "Missing or invalid internal API token."})

    request.state.authenticated_user_email = request.headers.get("x-authenticated-user-email")
    return await call_next(request)


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)
