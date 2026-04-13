from __future__ import annotations

from pydantic import BaseModel

from app.api.schemas.common import CandidateStatus


class DashboardTopCandidate(BaseModel):
    id: int | None
    name: str
    score: int
    status: CandidateStatus


class DashboardStatsResponse(BaseModel):
    total_cv: int
    matched_count: int
    pending_count: int
    reviewed_count: int
    average_score: int
    top_candidates: list[DashboardTopCandidate]
