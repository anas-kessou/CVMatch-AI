from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.schemas.breakdown import ScoreBreakdown
from app.api.schemas.candidates import CandidateInput, CandidateScore
from app.api.schemas.job_post import JobDescriptionInput


class ScoringRequest(BaseModel):
    job: JobDescriptionInput
    candidates: list[CandidateInput] = Field(default_factory=list)


class ScoringResponse(BaseModel):
    ranked_candidates: list[CandidateScore]
    count: int = Field(ge=0)


class ScoringParameters(BaseModel):
    technical_weight: float = Field(default=0.35, ge=0, le=1)
    experience_weight: float = Field(default=0.2, ge=0, le=1)
    education_weight: float = Field(default=0.15, ge=0, le=1)
    soft_skills_weight: float = Field(default=0.1, ge=0, le=1)
    semantic_weight: float = Field(default=0.2, ge=0, le=1)
    excellent_threshold: int = Field(default=85, ge=0, le=100)
    good_threshold: int = Field(default=70, ge=0, le=100)
