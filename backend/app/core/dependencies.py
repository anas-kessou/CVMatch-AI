from __future__ import annotations

from functools import lru_cache

from app.application.services.cv_parser_service import CvParserService
from app.application.services.cv_ai_analyzer_service import CvAiAnalyzerService
from app.application.services.ner_service import NerService
from app.application.services.scoring_service import ScoringService
from app.application.services.semantic_similarity_service import SemanticSimilarityService
from app.infrastructure.repositories.candidate_repository import CandidateRepository
from app.infrastructure.repositories.ingestion_job_repository import IngestionJobRepository
from app.infrastructure.repositories.job_repository import JobRepository


@lru_cache
def get_cv_parser_service() -> CvParserService:
    return CvParserService()


@lru_cache
def get_cv_ai_analyzer_service() -> CvAiAnalyzerService:
    return CvAiAnalyzerService()


@lru_cache
def get_ner_service() -> NerService:
    return NerService()


@lru_cache
def get_semantic_similarity_service() -> SemanticSimilarityService:
    return SemanticSimilarityService()


@lru_cache
def get_scoring_service() -> ScoringService:
    return ScoringService(
        ner_service=get_ner_service(),
        semantic_similarity_service=get_semantic_similarity_service(),
    )


@lru_cache
def get_job_repository() -> JobRepository:
    return JobRepository()


@lru_cache
def get_candidate_repository() -> CandidateRepository:
    return CandidateRepository()


@lru_cache
def get_ingestion_job_repository() -> IngestionJobRepository:
    return IngestionJobRepository()
