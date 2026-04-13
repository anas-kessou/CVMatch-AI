from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.api.schemas.cv import IngestionJobStatusResponse, UploadCvResponse, UploadedCvSummary


class IngestionJobRepository:
    def __init__(self, storage_file: Path | None = None) -> None:
        base_dir = Path(__file__).resolve().parents[3]
        data_dir = base_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.storage_file = storage_file or data_dir / "ingestion_jobs.json"
        self._lock = Lock()
        if not self.storage_file.exists():
            self.storage_file.write_text("{}", encoding="utf-8")

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _read_all(self) -> dict[str, dict[str, object]]:
        content = self.storage_file.read_text(encoding="utf-8").strip() or "{}"
        return json.loads(content)

    def _write_all(self, payload: dict[str, dict[str, object]]) -> None:
        self.storage_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def create_job(self, file_names: list[str]) -> IngestionJobStatusResponse:
        with self._lock:
            jobs = self._read_all()
            job_id = str(uuid4())
            now = self._now()
            jobs[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "created_at": now,
                "updated_at": now,
                "total_files": len(file_names),
                "processed_files": 0,
                "accepted": [],
                "rejected": [],
                "parsed_candidates": [],
                "error_message": None,
            }
            self._write_all(jobs)
            return IngestionJobStatusResponse(**jobs[job_id])

    def mark_processing(self, job_id: str) -> IngestionJobStatusResponse:
        return self._update(job_id, {"status": "processing", "updated_at": self._now()})

    def mark_failed(self, job_id: str, message: str) -> IngestionJobStatusResponse:
        return self._update(
            job_id,
            {
                "status": "failed",
                "updated_at": self._now(),
                "error_message": message,
            },
        )

    def mark_completed(self, job_id: str, upload_response: UploadCvResponse) -> IngestionJobStatusResponse:
        parsed_candidates = [item.model_dump() for item in upload_response.parsed_candidates]
        processed_total = len(upload_response.accepted) + len(upload_response.rejected)
        return self._update(
            job_id,
            {
                "status": "completed",
                "updated_at": self._now(),
                "processed_files": processed_total,
                "accepted": upload_response.accepted,
                "rejected": upload_response.rejected,
                "parsed_candidates": parsed_candidates,
                "error_message": None,
            },
        )

    def update_progress(
        self,
        job_id: str,
        processed_files: int,
        accepted: list[str],
        rejected: list[str],
        parsed_candidates: list[UploadedCvSummary],
    ) -> IngestionJobStatusResponse:
        return self._update(
            job_id,
            {
                "updated_at": self._now(),
                "processed_files": processed_files,
                "accepted": list(accepted),
                "rejected": list(rejected),
                "parsed_candidates": [item.model_dump() for item in parsed_candidates],
            },
        )

    def get_job(self, job_id: str) -> IngestionJobStatusResponse | None:
        with self._lock:
            jobs = self._read_all()
            job = jobs.get(job_id)
            if job is None:
                return None
            normalized = {
                **job,
                "parsed_candidates": [UploadedCvSummary(**item) for item in job.get("parsed_candidates", [])],
            }
            return IngestionJobStatusResponse(**normalized)

    def _update(self, job_id: str, fields: dict[str, object]) -> IngestionJobStatusResponse:
        with self._lock:
            jobs = self._read_all()
            if job_id not in jobs:
                raise KeyError(f"Job {job_id} not found")
            jobs[job_id].update(fields)
            self._write_all(jobs)
            normalized = {
                **jobs[job_id],
                "parsed_candidates": [UploadedCvSummary(**item) for item in jobs[job_id].get("parsed_candidates", [])],
            }
            return IngestionJobStatusResponse(**normalized)
