from __future__ import annotations

import asyncio

from app.api.schemas.score import ScoringRequest
from app.api.schemas.job_post import JobDescriptionInput
from app.api.schemas.candidates import CandidateInput
from app.application.services.ner_service import NerService
from app.application.services.scoring_service import ScoringService
from app.application.services.semantic_similarity_service import SemanticSimilarityService


async def main() -> None:
    service = ScoringService(
        ner_service=NerService(),
        semantic_similarity_service=SemanticSimilarityService(),
    )

    payload = ScoringRequest(
        job=JobDescriptionInput(
            title="Data Scientist",
            company="TechCorp",
            description="Python, ML, SQL, communication",
            required_hard_skills=["Python", "Machine Learning", "SQL"],
            required_soft_skills=["Communication", "Leadership"],
            min_experience=3,
            education_level="master",
        ),
        candidates=[
            CandidateInput(
                id=1,
                name="Alice",
                email="alice@example.com",
                raw_text="5 ans Python ML SQL leadership master",
            )
        ],
    )

    ranked = await service.score_candidates(payload.candidates, payload.job)
    print({"count": len(ranked), "top_score": ranked[0].score if ranked else 0})


if __name__ == "__main__":
    asyncio.run(main())
