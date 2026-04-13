from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile

from app.api.schemas.cv import (
    IngestionJobCreateResponse,
    IngestionJobStatusResponse,
    ParseCvRequest,
    ParsedCvResponse,
    UploadCvResponse,
)
from app.application.services.cv_ai_analyzer_service import CvAiAnalyzerService
from app.application.services.cv_parser_service import CvParserService
from app.application.services.ner_service import NerService
from app.application.use_cases.upload_cv_use_case import UploadCvUseCase
from app.core.dependencies import (
    get_cv_ai_analyzer_service,
    get_cv_parser_service,
    get_ingestion_job_repository,
    get_ner_service,
)

router = APIRouter(prefix="/cvs", tags=["cvs"])


def _process_ingestion_job(
    job_id: str,
    file_payloads: list[tuple[str, bytes]],
    cv_parser_service: CvParserService,
    ner_service: NerService,
    cv_ai_analyzer_service: CvAiAnalyzerService,
    ingestion_repository: Any,
) -> None:
    ingestion_repository.mark_processing(job_id)
    try:
        use_case = UploadCvUseCase(cv_parser_service, ner_service, cv_ai_analyzer_service)

        def on_progress(processed_files: int, accepted: list[str], rejected: list[str], parsed_candidates) -> None:
            ingestion_repository.update_progress(
                job_id=job_id,
                processed_files=processed_files,
                accepted=accepted,
                rejected=rejected,
                parsed_candidates=parsed_candidates,
            )

        result: UploadCvResponse = use_case.execute_from_payloads(file_payloads, progress_callback=on_progress)
        ingestion_repository.mark_completed(job_id, result)
    except Exception as exc:  # pragma: no cover - defensive fallback
        ingestion_repository.mark_failed(job_id, str(exc))


@router.post("/upload", response_model=IngestionJobCreateResponse)
async def upload_cv(
    background_tasks: BackgroundTasks,
    files: list[UploadFile] = File(...),
    cv_parser_service: CvParserService = Depends(get_cv_parser_service),
    ner_service: NerService = Depends(get_ner_service),
    cv_ai_analyzer_service: CvAiAnalyzerService = Depends(get_cv_ai_analyzer_service),
    ingestion_repository = Depends(get_ingestion_job_repository),
) -> IngestionJobCreateResponse:
    file_payloads = [(file.filename or "unknown", await file.read()) for file in files]
    job = ingestion_repository.create_job([name for name, _content in file_payloads])

    background_tasks.add_task(
        _process_ingestion_job,
        job.job_id,
        file_payloads,
        cv_parser_service,
        ner_service,
        cv_ai_analyzer_service,
        ingestion_repository,
    )
    return IngestionJobCreateResponse(job_id=job.job_id, status=job.status)


@router.get("/ingestion-jobs/{job_id}", response_model=IngestionJobStatusResponse)
def get_ingestion_job_status(
    job_id: str,
    ingestion_repository = Depends(get_ingestion_job_repository),
) -> IngestionJobStatusResponse:
    job = ingestion_repository.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Ingestion job not found")
    return job


@router.post("/parse", response_model=ParsedCvResponse)
def parse_cv(
    payload: ParseCvRequest,
    ner_service: NerService = Depends(get_ner_service),
    cv_ai_analyzer_service: CvAiAnalyzerService = Depends(get_cv_ai_analyzer_service),
) -> ParsedCvResponse:
    ai_profile = cv_ai_analyzer_service.analyze(payload.raw_text)
    if ai_profile is not None:
        return ai_profile
    return ner_service.parse_cv_text(payload.raw_text)
