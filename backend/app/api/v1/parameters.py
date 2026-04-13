from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas.score import ScoringParameters

router = APIRouter(prefix="/parameters", tags=["parameters"])

_CURRENT_PARAMETERS = ScoringParameters()


@router.get("/scoring", response_model=ScoringParameters)
def get_scoring_parameters() -> ScoringParameters:
    return _CURRENT_PARAMETERS


@router.put("/scoring", response_model=ScoringParameters)
def update_scoring_parameters(payload: ScoringParameters) -> ScoringParameters:
    global _CURRENT_PARAMETERS
    _CURRENT_PARAMETERS = payload
    return _CURRENT_PARAMETERS
