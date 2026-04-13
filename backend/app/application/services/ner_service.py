from __future__ import annotations

import re

from app.api.schemas.common import EducationLevel
from app.api.schemas.cv import ParsedCvResponse

SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "python": ("python", "py"),
    "machine learning": ("machine learning", "ml", "apprentissage automatique"),
    "deep learning": ("deep learning", "dl", "réseaux de neurones"),
    "tensorflow": ("tensorflow",),
    "pytorch": ("pytorch",),
    "sql": ("sql", "postgresql", "mysql"),
    "react": ("react", "reactjs", "react.js"),
    "nlp": ("nlp", "traitement du langage", "natural language processing"),
}

SOFT_SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "communication": ("communication",),
    "leadership": ("leadership", "management", "gestion d'équipe"),
    "travail d equipe": ("travail d equipe", "teamwork", "collaboration"),
    "resolution de problemes": (
        "resolution de problemes",
        "problem solving",
        "résolution de problèmes",
    ),
}


class NerService:
    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    def _extract_skills(self, raw_text: str, aliases: dict[str, tuple[str, ...]]) -> list[str]:
        text = self._normalize(raw_text)
        found: list[str] = []
        for canonical, patterns in aliases.items():
            if any(pattern in text for pattern in patterns):
                found.append(canonical)
        return found

    def _extract_experience_years(self, raw_text: str) -> int:
        text = self._normalize(raw_text)
        matches = re.findall(r"(\d{1,2})\s*(?:\+)?\s*(?:ans|years?)", text)
        if not matches:
            return 0
        return max(int(value) for value in matches)

    def _extract_education_level(self, raw_text: str) -> EducationLevel:
        text = self._normalize(raw_text)
        if any(token in text for token in ("doctorat", "phd", "doctorate")):
            return "doctorat"
        if any(token in text for token in ("master", "bac+5", "msc")):
            return "master"
        if any(token in text for token in ("licence", "license", "bachelor", "bac+3")):
            return "license"
        if any(token in text for token in ("bac", "high school")):
            return "none"
        return "other"

    def parse_cv_text(self, raw_text: str) -> ParsedCvResponse:
        return ParsedCvResponse(
            hard_skills=self._extract_skills(raw_text, SKILL_ALIASES),
            soft_skills=self._extract_skills(raw_text, SOFT_SKILL_ALIASES),
            experience_years=self._extract_experience_years(raw_text),
            education_level=self._extract_education_level(raw_text),
        )
