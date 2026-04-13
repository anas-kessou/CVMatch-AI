from __future__ import annotations

from pydantic import BaseModel, Field

from app.api.schemas.common import EducationLevel


class JobDescriptionInput(BaseModel):
    title: str = Field(min_length=2)
    company: str = Field(min_length=2)
    description: str = Field(min_length=10)
    required_hard_skills: list[str] = Field(default_factory=list)
    required_soft_skills: list[str] = Field(default_factory=list)
    min_experience: int = Field(default=0, ge=0, le=40)
    education_level: EducationLevel = "other"
