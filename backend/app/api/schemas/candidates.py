from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.api.schemas.common import CandidateStatus, EducationLevel
from app.api.schemas.breakdown import ScoreBreakdown


class CandidateInput(BaseModel):
    class ExperienceItem(BaseModel):
        title: str
        company: str | None = None
        duration: str | None = None

    class EducationItem(BaseModel):
        degree: str
        school: str | None = None
        year: str | None = None

    id: int | None = None
    name: str = Field(min_length=2)
    email: EmailStr | None = None
    phone: str | None = None
    location: str | None = None
    headline: str | None = None
    summary: str | None = None
    raw_text: str = Field(default="", description="Texte brut extrait du CV")
    hard_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    experience_years: int | None = Field(default=None, ge=0, le=50)
    education_level: EducationLevel | None = None
    experiences: list[ExperienceItem] = Field(default_factory=list)
    educations: list[EducationItem] = Field(default_factory=list)


class CandidateScore(BaseModel):
    id: int | None = None
    name: str
    email: EmailStr | None = None
    score: int = Field(ge=0, le=100)
    status: CandidateStatus
    extracted_hard_skills: list[str] = Field(default_factory=list)
    extracted_soft_skills: list[str] = Field(default_factory=list)
    extracted_experience_years: int = Field(ge=0)
    extracted_education_level: EducationLevel
    match_details: ScoreBreakdown
    rationale: str
