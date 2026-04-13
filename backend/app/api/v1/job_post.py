from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas.job_post import JobDescriptionInput
from app.core.dependencies import get_job_repository
from app.domain.entities.job_post import JobPost
from app.infrastructure.repositories.job_repository import JobRepository

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobDescriptionInput)
def create_or_update_job(
    payload: JobDescriptionInput,
    repository: JobRepository = Depends(get_job_repository),
) -> JobDescriptionInput:
    saved = repository.save(
        JobPost(
            title=payload.title,
            company=payload.company,
            description=payload.description,
            required_hard_skills=payload.required_hard_skills,
            required_soft_skills=payload.required_soft_skills,
            min_experience=payload.min_experience,
            education_level=payload.education_level,
        )
    )
    return JobDescriptionInput(
        title=saved.title,
        company=saved.company,
        description=saved.description,
        required_hard_skills=saved.required_hard_skills,
        required_soft_skills=saved.required_soft_skills,
        min_experience=saved.min_experience,
        education_level=saved.education_level,
    )
