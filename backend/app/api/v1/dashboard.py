from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.schemas.dashboard import DashboardStatsResponse
from app.application.use_cases.get_dashboard_use_case import GetDashboardUseCase
from app.core.dependencies import get_candidate_repository
from app.infrastructure.repositories.candidate_repository import CandidateRepository

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(
    candidate_repository: CandidateRepository = Depends(get_candidate_repository),
) -> DashboardStatsResponse:
    return GetDashboardUseCase(candidate_repository).execute()
