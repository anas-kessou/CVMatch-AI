from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.candidates import router as candidates_router
from app.api.v1.cv import router as cv_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.health import router as health_router
from app.api.v1.job_post import router as job_router
from app.api.v1.parameters import router as parameters_router
from app.api.v1.scoring import router as scoring_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(scoring_router)
api_router.include_router(dashboard_router)
api_router.include_router(job_router)
api_router.include_router(cv_router)
api_router.include_router(candidates_router)
api_router.include_router(analytics_router)
api_router.include_router(parameters_router)
