from __future__ import annotations

from app.domain.entities.score import CandidateScoreEntity


class CandidateRepository:
    def __init__(self) -> None:
        self._scores: list[CandidateScoreEntity] = []

    def save_scored_candidates(self, scores: list[CandidateScoreEntity]) -> list[CandidateScoreEntity]:
        self._scores = list(scores)
        return self._scores

    def list_scored_candidates(self) -> list[CandidateScoreEntity]:
        return list(self._scores)
