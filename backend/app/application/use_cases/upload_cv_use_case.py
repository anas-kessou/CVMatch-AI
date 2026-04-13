from __future__ import annotations

from pathlib import Path
from typing import Callable

from fastapi import UploadFile

from app.api.schemas.candidates import CandidateInput
from app.api.schemas.cv import UploadCvResponse, UploadedCvSummary
from app.application.services.cv_ai_analyzer_service import CvAiAnalyzerService
from app.application.services.cv_parser_service import CvParserService
from app.application.services.ner_service import NerService


class UploadCvUseCase:
    def __init__(
        self,
        cv_parser_service: CvParserService,
        ner_service: NerService,
        cv_ai_analyzer_service: CvAiAnalyzerService | None = None,
    ) -> None:
        self.cv_parser_service = cv_parser_service
        self.ner_service = ner_service
        self.cv_ai_analyzer_service = cv_ai_analyzer_service or CvAiAnalyzerService()

    async def execute(self, files: list[UploadFile]) -> UploadCvResponse:
        payloads: list[tuple[str, bytes]] = []
        for file in files:
            payloads.append((file.filename or "unknown", await file.read()))
        return self.execute_from_payloads(payloads)

    def execute_from_payloads(
        self,
        file_payloads: list[tuple[str, bytes]],
        progress_callback: Callable[[int, list[str], list[str], list[UploadedCvSummary]], None] | None = None,
    ) -> UploadCvResponse:
        accepted: list[str] = []
        rejected: list[str] = []
        parsed_candidates: list[UploadedCvSummary] = []

        candidate_id = 1
        processed_files = 0
        for file_name, content in file_payloads:
            if not file_name.lower().endswith((".pdf", ".docx")):
                rejected.append(file_name)
                processed_files += 1
                if progress_callback is not None:
                    progress_callback(processed_files, accepted, rejected, parsed_candidates)
                continue

            if not content:
                rejected.append(file_name)
                processed_files += 1
                if progress_callback is not None:
                    progress_callback(processed_files, accepted, rejected, parsed_candidates)
                continue

            try:
                extracted_text = self.cv_parser_service.extract_text(file_name, content)
            except Exception:
                rejected.append(file_name)
                processed_files += 1
                if progress_callback is not None:
                    progress_callback(processed_files, accepted, rejected, parsed_candidates)
                continue

            if not extracted_text.strip():
                rejected.append(file_name)
                processed_files += 1
                if progress_callback is not None:
                    progress_callback(processed_files, accepted, rejected, parsed_candidates)
                continue

            parsed = self.ner_service.parse_cv_text(extracted_text)
            ai_profile = self.cv_ai_analyzer_service.analyze(extracted_text)

            stem_name = Path(file_name).stem.replace("_", " ").replace("-", " ").strip() or "Candidat"

            hard_skills = ai_profile.hard_skills if ai_profile and ai_profile.hard_skills else parsed.hard_skills
            soft_skills = ai_profile.soft_skills if ai_profile and ai_profile.soft_skills else parsed.soft_skills
            experience_years = (
                ai_profile.experience_years
                if ai_profile is not None and ai_profile.experience_years > 0
                else parsed.experience_years
            )
            education_level = (
                ai_profile.education_level
                if ai_profile is not None and ai_profile.education_level != "other"
                else parsed.education_level
            )

            candidate = CandidateInput(
                id=candidate_id,
                name=(ai_profile.name if ai_profile and ai_profile.name else stem_name).title(),
                email=ai_profile.email if ai_profile else None,
                phone=ai_profile.phone if ai_profile else None,
                location=ai_profile.location if ai_profile else None,
                headline=ai_profile.headline if ai_profile else None,
                summary=ai_profile.summary if ai_profile else None,
                raw_text=extracted_text,
                hard_skills=hard_skills,
                soft_skills=soft_skills,
                experience_years=experience_years,
                education_level=education_level,
                experiences=ai_profile.experiences if ai_profile else [],
                educations=ai_profile.educations if ai_profile else [],
            )

            parsed_candidates.append(UploadedCvSummary(file_name=file_name, candidate=candidate))
            accepted.append(file_name)
            candidate_id += 1
            processed_files += 1

            if progress_callback is not None:
                progress_callback(processed_files, accepted, rejected, parsed_candidates)

        return UploadCvResponse(
            accepted=accepted,
            rejected=rejected,
            count=len(accepted),
            parsed_candidates=parsed_candidates,
        )
