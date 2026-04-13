from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.app_env,
        "ollama_enabled": str(settings.ollama_enabled).lower(),
        "ollama_model": settings.ollama_model,
    }
