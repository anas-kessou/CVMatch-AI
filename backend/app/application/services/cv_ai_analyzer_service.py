from __future__ import annotations

import json
import re

import httpx

from app.api.schemas.common import EducationLevel
from app.api.schemas.cv import ParsedCvResponse
from app.core.config import settings


class CvAiAnalyzerService:
    @staticmethod
    def _normalize_education_level(value: str | None) -> EducationLevel:
        normalized = (value or "").strip().lower()
        if normalized in {"doctorat", "phd", "doctorate"}:
            return "doctorat"
        if normalized in {"master", "msc", "bac+5"}:
            return "master"
        if normalized in {"license", "licence", "bachelor", "bac+3"}:
            return "license"
        if normalized in {"none", "bac", "high school", "lycee"}:
            return "none"
        return "other"

    @staticmethod
    def _sanitize_string(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        cleaned = re.sub(r"\s+", " ", value).strip()
        return cleaned or None

    @staticmethod
    def _sanitize_str_list(value: object) -> list[str]:
        if not isinstance(value, list):
            return []
        output: list[str] = []
        for item in value:
            if not isinstance(item, str):
                continue
            cleaned = re.sub(r"\s+", " ", item).strip()
            if cleaned and cleaned not in output:
                output.append(cleaned)
        return output

    def _build_prompt(self, raw_text: str) -> str:
        return (
            "Analyse ce CV et retourne UNIQUEMENT un JSON compact valide avec exactement ces clés: "
            "name, email, phone, location, headline, summary, hard_skills, soft_skills, "
            "experience_years, education_level, experiences, educations. "
            "- hard_skills et soft_skills: tableaux de chaînes. "
            "- experience_years: entier >= 0. "
            "- education_level: one of [none, license, master, doctorat, other]. "
            "- experiences: tableau d'objets {title, company, duration}. "
            "- educations: tableau d'objets {degree, school, year}. "
            "Si une information manque, utilise null ou tableau vide.\n\n"
            f"CV:\n{raw_text}"
        )

    def analyze(self, raw_text: str) -> ParsedCvResponse | None:
        if not settings.ollama_enabled:
            return None

        payload = {
            "model": settings.ollama_model,
            "prompt": self._build_prompt(raw_text),
            "stream": False,
            "format": "json",
        }
        url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"

        try:
            with httpx.Client(timeout=settings.ollama_timeout_seconds) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()

            generated = data.get("response", "")
            parsed = json.loads(generated)

            experiences_raw = parsed.get("experiences", [])
            educations_raw = parsed.get("educations", [])

            experiences = []
            if isinstance(experiences_raw, list):
                for item in experiences_raw:
                    if isinstance(item, dict):
                        title = self._sanitize_string(item.get("title"))
                        if not title:
                            continue
                        experiences.append(
                            {
                                "title": title,
                                "company": self._sanitize_string(item.get("company")),
                                "duration": self._sanitize_string(item.get("duration")),
                            }
                        )

            educations = []
            if isinstance(educations_raw, list):
                for item in educations_raw:
                    if isinstance(item, dict):
                        degree = self._sanitize_string(item.get("degree"))
                        if not degree:
                            continue
                        educations.append(
                            {
                                "degree": degree,
                                "school": self._sanitize_string(item.get("school")),
                                "year": self._sanitize_string(item.get("year")),
                            }
                        )

            experience_years_raw = parsed.get("experience_years", 0)
            try:
                experience_years = max(0, int(experience_years_raw))
            except Exception:
                experience_years = 0

            return ParsedCvResponse(
                name=self._sanitize_string(parsed.get("name")),
                email=self._sanitize_string(parsed.get("email")),
                phone=self._sanitize_string(parsed.get("phone")),
                location=self._sanitize_string(parsed.get("location")),
                headline=self._sanitize_string(parsed.get("headline")),
                summary=self._sanitize_string(parsed.get("summary")),
                hard_skills=self._sanitize_str_list(parsed.get("hard_skills")),
                soft_skills=self._sanitize_str_list(parsed.get("soft_skills")),
                experience_years=experience_years,
                education_level=self._normalize_education_level(self._sanitize_string(parsed.get("education_level"))),
                experiences=experiences,
                educations=educations,
            )
        except Exception:
            return None
