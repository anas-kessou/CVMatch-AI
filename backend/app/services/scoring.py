from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass

import httpx

from app.config import settings
from app.schemas import (
    CandidateInput,
    CandidateScore,
    EducationLevel,
    JobDescriptionInput,
    ParsedCvResponse,
    ScoreBreakdown,
)

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

EDUCATION_ORDER: dict[EducationLevel, int] = {
    "none": 0,
    "license": 1,
    "master": 2,
    "doctorat": 3,
    "other": 1,
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _extract_skills(raw_text: str, aliases: dict[str, tuple[str, ...]]) -> list[str]:
    text = _normalize(raw_text)
    found: list[str] = []
    for canonical, patterns in aliases.items():
        if any(pattern in text for pattern in patterns):
            found.append(canonical)
    return found


def _extract_experience_years(raw_text: str) -> int:
    text = _normalize(raw_text)
    matches = re.findall(r"(\d{1,2})\s*(?:\+)?\s*(?:ans|years?)", text)
    if not matches:
        return 0
    values = [int(value) for value in matches]
    return max(values)


def _extract_education_level(raw_text: str) -> EducationLevel:
    text = _normalize(raw_text)
    if any(token in text for token in ("doctorat", "phd", "doctorate")):
        return "doctorat"
    if any(token in text for token in ("master", "bac+5", "msc")):
        return "master"
    if any(token in text for token in ("licence", "license", "bachelor", "bac+3")):
        return "license"
    if any(token in text for token in ("bac", "high school")):
        return "none"
    return "other"


def parse_cv_text(raw_text: str) -> ParsedCvResponse:
    return ParsedCvResponse(
        hard_skills=_extract_skills(raw_text, SKILL_ALIASES),
        soft_skills=_extract_skills(raw_text, SOFT_SKILL_ALIASES),
        experience_years=_extract_experience_years(raw_text),
        education_level=_extract_education_level(raw_text),
    )


@dataclass
class OllamaSimilarityResult:
    score: int
    rationale: str


async def _ollama_semantic_similarity(cv_text: str, jd_text: str) -> OllamaSimilarityResult | None:
    if not settings.ollama_enabled:
        return None

    prompt = (
        "Tu es un moteur de matching CV. Retourne UNIQUEMENT un JSON compact avec les clés: "
        '"score" (0-100 entier) et "rationale" (max 25 mots). '\
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
    except Exception:
        return None

    generated = data.get("response", "")
    try:
        parsed = json.loads(generated)
        score = int(parsed.get("score", 0))
        rationale = str(parsed.get("rationale", "Aucune explication fournie"))
        score = min(100, max(0, score))
        return OllamaSimilarityResult(score=score, rationale=rationale)
    except Exception:
        return None


def _jaccard_score(values_a: list[str], values_b: list[str]) -> int:
    set_a = {_normalize(v) for v in values_a if v.strip()}
    set_b = {_normalize(v) for v in values_b if v.strip()}
    if not set_a and not set_b:
        return 0
    if not set_a or not set_b:
        return 0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return round((intersection / union) * 100)


def _experience_score(candidate_years: int, min_years: int) -> int:
    if min_years <= 0:
        return 100 if candidate_years > 0 else 60
    ratio = candidate_years / min_years
    return min(100, max(0, round(ratio * 100)))


def _education_score(candidate_level: EducationLevel, required_level: EducationLevel) -> int:
    candidate_rank = EDUCATION_ORDER.get(candidate_level, 1)
    required_rank = EDUCATION_ORDER.get(required_level, 1)
    if candidate_rank >= required_rank:
        return 100
    return max(0, 100 - ((required_rank - candidate_rank) * 30))


async def score_one_candidate(
    candidate: CandidateInput,
    job: JobDescriptionInput,
) -> CandidateScore:
    parsed = parse_cv_text(candidate.raw_text)
    hard_skills = candidate.hard_skills or parsed.hard_skills
    soft_skills = candidate.soft_skills or parsed.soft_skills
    experience_years = (
        candidate.experience_years
        if candidate.experience_years is not None
        else parsed.experience_years
    )
    education_level = candidate.education_level or parsed.education_level

    technical = _jaccard_score(hard_skills, job.required_hard_skills)
    soft = _jaccard_score(soft_skills, job.required_soft_skills)
    experience = _experience_score(experience_years, job.min_experience)
    education = _education_score(education_level, job.education_level)

    semantic_default = round((technical * 0.7) + (soft * 0.3))
    rationale = "Score calculé avec matching lexical + règles pondérées"
    ollama_result = await _ollama_semantic_similarity(candidate.raw_text, job.description)
    semantic = semantic_default
    if ollama_result is not None:
        semantic = ollama_result.score
        rationale = ollama_result.rationale

    final_score = round(
        (technical * 0.35)
        + (experience * 0.2)
        + (education * 0.15)
        + (soft * 0.1)
        + (semantic * 0.2)
    )

    status = "matched" if final_score >= 85 else "pending" if final_score >= 70 else "reviewed"

    return CandidateScore(
        id=candidate.id,
        name=candidate.name,
        email=candidate.email,
        score=min(100, max(0, final_score)),
        status=status,
        extracted_hard_skills=hard_skills,
        extracted_soft_skills=soft_skills,
        extracted_experience_years=max(0, experience_years),
        extracted_education_level=education_level,
        match_details=ScoreBreakdown(
            technical=technical,
            experience=experience,
            education=education,
            soft_skills=soft,
            semantic=semantic,
        ),
        rationale=rationale,
    )


async def score_candidates(candidates: list[CandidateInput], job: JobDescriptionInput) -> list[CandidateScore]:
    tasks = [score_one_candidate(candidate, job) for candidate in candidates]
    scores = await asyncio.gather(*tasks)
    return sorted(scores, key=lambda entry: entry.score, reverse=True)
