from __future__ import annotations

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    technical: int = Field(ge=0, le=100)
    experience: int = Field(ge=0, le=100)
    education: int = Field(ge=0, le=100)
    soft_skills: int = Field(ge=0, le=100)
    semantic: int = Field(ge=0, le=100)
