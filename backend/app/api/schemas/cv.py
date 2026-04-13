from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.api.schemas.candidates import CandidateInput
from app.api.schemas.common import EducationLevel


class ParseCvRequest(BaseModel):
    raw_text: str = Field(min_length=20)


class ParsedCvResponse(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    headline: str | None = None
    summary: str | None = None
    hard_skills: list[str]
    soft_skills: list[str]
    experience_years: int
    education_level: EducationLevel
    experiences: list[CandidateInput.ExperienceItem] = Field(default_factory=list)
    educations: list[CandidateInput.EducationItem] = Field(default_factory=list)


class UploadedCvSummary(BaseModel):
    file_name: str
    candidate: CandidateInput


class UploadCvResponse(BaseModel):
    accepted: list[str]
    rejected: list[str]
    count: int
    parsed_candidates: list[UploadedCvSummary]


IngestionJobStatus = Literal["queued", "processing", "completed", "failed"]


class IngestionJobCreateResponse(BaseModel):
    job_id: str
    status: IngestionJobStatus


class IngestionJobStatusResponse(BaseModel):
    job_id: str
    status: IngestionJobStatus
    created_at: str
    updated_at: str
    total_files: int
    processed_files: int
    accepted: list[str] = Field(default_factory=list)
    rejected: list[str] = Field(default_factory=list)
    parsed_candidates: list[UploadedCvSummary] = Field(default_factory=list)
    error_message: str | None = None
