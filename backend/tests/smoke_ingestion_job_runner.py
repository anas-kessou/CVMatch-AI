from __future__ import annotations

from pathlib import Path

from app.api.schemas.candidates import CandidateInput
from app.api.schemas.cv import UploadCvResponse, UploadedCvSummary
from app.infrastructure.repositories.ingestion_job_repository import IngestionJobRepository


def main() -> None:
    storage = Path(__file__).resolve().parent / "tmp_ingestion_jobs.json"
    if storage.exists():
        storage.unlink()

    repository = IngestionJobRepository(storage_file=storage)
    created = repository.create_job(["one.pdf", "two.docx"])
    repository.mark_processing(created.job_id)

    completed = repository.mark_completed(
        created.job_id,
        UploadCvResponse(
            accepted=["one.pdf"],
            rejected=["two.docx"],
            count=1,
            parsed_candidates=[
                UploadedCvSummary(
                    file_name="one.pdf",
                    candidate=CandidateInput(
                        id=1,
                        name="One",
                        email=None,
                        raw_text="Python SQL 3 ans master",
                        hard_skills=["python", "sql"],
                        soft_skills=[],
                        experience_years=3,
                        education_level="master",
                    ),
                )
            ],
        ),
    )

    reloaded = repository.get_job(created.job_id)
    print(
        {
            "status": completed.status,
            "persisted": reloaded.status if reloaded else None,
            "accepted": reloaded.accepted if reloaded else [],
        }
    )

    if storage.exists():
        storage.unlink()


if __name__ == "__main__":
    main()
