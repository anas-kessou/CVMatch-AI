from __future__ import annotations

import asyncio

from app.api.schemas.candidates import CandidateInput, CandidateScore
from app.api.schemas.common import EducationLevel
from app.api.schemas.job_post import JobDescriptionInput
from app.api.schemas.score import ScoreBreakdown
from app.application.services.ner_service import NerService
from app.application.services.semantic_similarity_service import SemanticSimilarityService

EDUCATION_ORDER: dict[EducationLevel, int] = {
    "none": 0,
    "license": 1,
    "master": 2,
    "doctorat": 3,
    "other": 1,
}


class ScoringService:
    def __init__(
        self,
        ner_service: NerService,
        semantic_similarity_service: SemanticSimilarityService,
    ) -> None:
        self.ner_service = ner_service
        self.semantic_similarity_service = semantic_similarity_service

    @staticmethod
    def _normalize(text: str) -> str:
        return text.strip().lower()

    def _jaccard_score(self, values_a: list[str], values_b: list[str]) -> int:
        set_a = {self._normalize(v) for v in values_a if v.strip()}
        set_b = {self._normalize(v) for v in values_b if v.strip()}
        if not set_a or not set_b:
            return 0
        return round((len(set_a.intersection(set_b)) / len(set_a.union(set_b))) * 100)

    @staticmethod
    def _experience_score(candidate_years: int, min_years: int) -> int:
        if min_years <= 0:
            return 100 if candidate_years > 0 else 60
        return min(100, max(0, round((candidate_years / min_years) * 100)))

    def _education_score(self, candidate_level: EducationLevel, required_level: EducationLevel) -> int:
        candidate_rank = EDUCATION_ORDER.get(candidate_level, 1)
        required_rank = EDUCATION_ORDER.get(required_level, 1)
        if candidate_rank >= required_rank:
            return 100
        return max(0, 100 - ((required_rank - candidate_rank) * 30))

    async def score_one_candidate(self, candidate: CandidateInput, job: JobDescriptionInput) -> CandidateScore:
        parsed = self.ner_service.parse_cv_text(candidate.raw_text)
        hard_skills = candidate.hard_skills or parsed.hard_skills
        soft_skills = candidate.soft_skills or parsed.soft_skills
        experience_years = candidate.experience_years if candidate.experience_years is not None else parsed.experience_years
        education_level = candidate.education_level or parsed.education_level

        technical = self._jaccard_score(hard_skills, job.required_hard_skills)
        soft = self._jaccard_score(soft_skills, job.required_soft_skills)
        experience = self._experience_score(experience_years, job.min_experience)
        education = self._education_score(education_level, job.education_level)
        semantic = round((technical * 0.7) + (soft * 0.3))
        rationale = "Score calculé avec matching lexical + règles pondérées"

        llm_score = await self.semantic_similarity_service.compute_semantic_score(
            cv_text=candidate.raw_text,
            jd_text=job.description,
        )
        if llm_score is not None:
            semantic, rationale = llm_score

        final_score = round(
            (technical * 0.35)
            + (experience * 0.2)
            + (education * 0.15)
            + (soft * 0.1)
            + (semantic * 0.2)
        )
        status = "matched" if final_score >= 85 else "pending" if final_score >= 70 else "reviewed"

        return CandidateScore(
            id=candidate.id,
            name=candidate.name,
            email=candidate.email,
            score=min(100, max(0, final_score)),
            status=status,
            extracted_hard_skills=hard_skills,
            extracted_soft_skills=soft_skills,
            extracted_experience_years=max(0, experience_years),
            extracted_education_level=education_level,
            match_details=ScoreBreakdown(
                technical=technical,
                experience=experience,
                education=education,
                soft_skills=soft,
                semantic=semantic,
            ),
            rationale=rationale,
        )

    async def score_candidates(self, candidates: list[CandidateInput], job: JobDescriptionInput) -> list[CandidateScore]:
        tasks = [self.score_one_candidate(candidate, job) for candidate in candidates]
        results = await asyncio.gather(*tasks)
        return sorted(results, key=lambda item: item.score, reverse=True)
