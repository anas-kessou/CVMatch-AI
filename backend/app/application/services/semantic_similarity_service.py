from __future__ import annotations

import json

import httpx

from app.core.config import settings


class SemanticSimilarityService:
    async def compute_semantic_score(self, cv_text: str, jd_text: str) -> tuple[int, str] | None:
        if not settings.ollama_enabled:
            return None

        prompt = (
            "Tu es un moteur de matching CV. Retourne UNIQUEMENT un JSON compact avec les clés: "
            '"score" (0-100 entier) et "rationale" (max 25 mots). '
            "Compare ce CV à la fiche de poste sur la pertinence globale.\n"
            f"Fiche de poste:\n{jd_text}\n\nCV:\n{cv_text}"
        )
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"

        try:
            async with httpx.AsyncClient(timeout=settings.ollama_timeout_seconds) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
            generated = data.get("response", "")
            parsed = json.loads(generated)
            score = int(parsed.get("score", 0))
            rationale = str(parsed.get("rationale", "Aucune explication fournie"))
            return min(100, max(0, score)), rationale
        except Exception:
            return None
