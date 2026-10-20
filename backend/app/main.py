"""FinGuard FastAPI Application."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown."""
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="FinGuard API",
    description="Multilingual AI Personal Finance Agent — Analyze financial documents, assess risks, and provide financial insights.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0", "service": "finguard-api"}
