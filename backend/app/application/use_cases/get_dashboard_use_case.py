from __future__ import annotations

from app.api.schemas.dashboard import DashboardStatsResponse
from app.infrastructure.repositories.candidate_repository import CandidateRepository


class GetDashboardUseCase:
    def __init__(self, candidate_repository: CandidateRepository) -> None:
        self.candidate_repository = candidate_repository

    def execute(self) -> DashboardStatsResponse:
        candidates = self.candidate_repository.list_scored_candidates()
        total = len(candidates)
        if total == 0:
            return DashboardStatsResponse(
                total_cv=0,
                matched_count=0,
                pending_count=0,
                reviewed_count=0,
                average_score=0,
                top_candidates=[],
            )

        matched = len([c for c in candidates if c.status == "matched"])
        pending = len([c for c in candidates if c.status == "pending"])
        reviewed = len([c for c in candidates if c.status == "reviewed"])
        avg = round(sum(c.score for c in candidates) / total)
        top = sorted(candidates, key=lambda c: c.score, reverse=True)[:5]

        return DashboardStatsResponse(
            total_cv=total,
            matched_count=matched,
            pending_count=pending,
            reviewed_count=reviewed,
            average_score=avg,
            top_candidates=[
                {
                    "id": c.id,
                    "name": c.name,
                    "score": c.score,
                    "status": c.status,
                }
                for c in top
            ],
        )
