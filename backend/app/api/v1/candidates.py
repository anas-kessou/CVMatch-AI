from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas.candidates import CandidateScore
from app.core.dependencies import get_candidate_repository
from app.infrastructure.repositories.candidate_repository import CandidateRepository

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/", response_model=list[CandidateScore])
def list_candidates(
    repository: CandidateRepository = Depends(get_candidate_repository),
) -> list[CandidateScore]:
    return [
        CandidateScore(
            id=c.id,
            name=c.name,
            email=c.email,
            score=c.score,
            status=c.status,
            extracted_hard_skills=c.extracted_hard_skills,
            extracted_soft_skills=c.extracted_soft_skills,
            extracted_experience_years=c.extracted_experience_years,
            extracted_education_level=c.extracted_education_level,
            match_details={
                "technical": c.match_details.technical,
                "experience": c.match_details.experience,
                "education": c.match_details.education,
                "soft_skills": c.match_details.soft_skills,
                "semantic": c.match_details.semantic,
            },
            rationale=c.rationale,
        )
        for c in repository.list_scored_candidates()
    ]
