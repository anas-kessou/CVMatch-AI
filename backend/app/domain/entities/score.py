from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ScoreBreakdownEntity:
    technical: int
    experience: int
    education: int
    soft_skills: int
    semantic: int


@dataclass(slots=True)
class CandidateScoreEntity:
    id: int | None
    name: str
    email: str | None
    score: int
    status: str
    extracted_hard_skills: list[str] = field(default_factory=list)
    extracted_soft_skills: list[str] = field(default_factory=list)
    extracted_experience_years: int = 0
    extracted_education_level: str = "other"
    rationale: str = ""
    match_details: ScoreBreakdownEntity = field(
        default_factory=lambda: ScoreBreakdownEntity(0, 0, 0, 0, 0)
    )
