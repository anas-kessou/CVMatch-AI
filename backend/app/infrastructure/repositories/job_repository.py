from __future__ import annotations

from app.domain.entities.job_post import JobPost


class JobRepository:
    def __init__(self) -> None:
        self._job: JobPost | None = None

    def save(self, job: JobPost) -> JobPost:
        self._job = job
        return self._job

    def get_current(self) -> JobPost | None:
        return self._job
