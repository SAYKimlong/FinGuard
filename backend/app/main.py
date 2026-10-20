"""FinGuard FastAPI Application."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    yield


is_production = settings.APP_ENV.strip().lower() in {"production", "prod"}
app = FastAPI(
    title="FinGuard API",
    description="Multilingual AI Personal Finance Agent — Analyze financial documents, assess risks, and provide financial insights.",
    version="1.0.0",
    docs_url=None if is_production else "/docs",
    redoc_url=None if is_production else "/redoc",
    openapi_url=None if is_production else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next) -> Response:
    """Set baseline browser security headers on every API response."""
    response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("Cache-Control", "no-store")
    if is_production:
        response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


# Import and register routers
from app.api.auth.router import router as auth_router
from app.api.documents.router import router as documents_router
from app.api.financial.router import router as financial_router
from app.api.chat.router import router as chat_router
from app.api.reports.router import router as reports_router

app.include_router(auth_router)
app.include_router(documents_router, prefix="/api/documents")
app.include_router(financial_router, prefix="/api/financial")
app.include_router(chat_router, prefix="/api/chat")
app.include_router(reports_router, prefix="/api/reports")


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Minimal liveness endpoint; does not disclose internal dependency state."""
    return {"status": "healthy"}
