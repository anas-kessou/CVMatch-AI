from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas.score import ScoringRequest, ScoringResponse
from app.application.use_cases.calculate_score_use_case import CalculateScoreUseCase
from app.core.dependencies import get_candidate_repository, get_scoring_service
from app.application.services.scoring_service import ScoringService
from app.infrastructure.repositories.candidate_repository import CandidateRepository

router = APIRouter(tags=["scoring"])


@router.post("/score", response_model=ScoringResponse)
async def score_candidates_endpoint(
    payload: ScoringRequest,
    scoring_service: ScoringService = Depends(get_scoring_service),
    candidate_repository: CandidateRepository = Depends(get_candidate_repository),
) -> ScoringResponse:
    ranked_candidates = await CalculateScoreUseCase(scoring_service, candidate_repository).execute(payload)
    return ScoringResponse(ranked_candidates=ranked_candidates, count=len(ranked_candidates))
