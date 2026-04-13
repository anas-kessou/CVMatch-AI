from __future__ import annotations

from app.api.schemas.candidates import CandidateScore
from app.api.schemas.job_post import JobDescriptionInput
from app.api.schemas.score import ScoringRequest
from app.application.services.scoring_service import ScoringService
from app.domain.entities.score import CandidateScoreEntity, ScoreBreakdownEntity
from app.infrastructure.repositories.candidate_repository import CandidateRepository


class CalculateScoreUseCase:
    def __init__(self, scoring_service: ScoringService, candidate_repository: CandidateRepository) -> None:
        self.scoring_service = scoring_service
        self.candidate_repository = candidate_repository

    async def execute(self, payload: ScoringRequest) -> list[CandidateScore]:
        scores = await self.scoring_service.score_candidates(payload.candidates, payload.job)
        self.candidate_repository.save_scored_candidates(
            [
                CandidateScoreEntity(
                    id=score.id,
                    name=score.name,
                    email=score.email,
                    score=score.score,
                    status=score.status,
                    extracted_hard_skills=score.extracted_hard_skills,
                    extracted_soft_skills=score.extracted_soft_skills,
                    extracted_experience_years=score.extracted_experience_years,
                    extracted_education_level=score.extracted_education_level,
                    rationale=score.rationale,
                    match_details=ScoreBreakdownEntity(
                        technical=score.match_details.technical,
                        experience=score.match_details.experience,
                        education=score.match_details.education,
                        soft_skills=score.match_details.soft_skills,
                        semantic=score.match_details.semantic,
                    ),
                )
                for score in scores
            ]
        )
        return scores
