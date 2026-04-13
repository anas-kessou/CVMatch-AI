from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas.analytics import AnalyticsResponse, RangeBucket
from app.core.dependencies import get_candidate_repository
from app.infrastructure.repositories.candidate_repository import CandidateRepository

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/", response_model=AnalyticsResponse)
def get_analytics(
    repository: CandidateRepository = Depends(get_candidate_repository),
) -> AnalyticsResponse:
    candidates = repository.list_scored_candidates()
    score_distribution = [
        RangeBucket(range="90-100%", count=len([c for c in candidates if c.score >= 90])),
        RangeBucket(range="75-89%", count=len([c for c in candidates if 75 <= c.score < 90])),
        RangeBucket(range="60-74%", count=len([c for c in candidates if 60 <= c.score < 75])),
        RangeBucket(range="<60%", count=len([c for c in candidates if c.score < 60])),
    ]
    status_distribution = [
        RangeBucket(range="matched", count=len([c for c in candidates if c.status == "matched"])),
        RangeBucket(range="pending", count=len([c for c in candidates if c.status == "pending"])),
        RangeBucket(range="reviewed", count=len([c for c in candidates if c.status == "reviewed"])),
    ]
    return AnalyticsResponse(
        score_distribution=score_distribution,
        status_distribution=status_distribution,
    )
