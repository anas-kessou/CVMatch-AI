from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.database import Base

class ScoringResult(Base):
    __tablename__ = "scoring_results"
    id = Column(Integer, primary_key=True, index=True)
    candidate_profile_id = Column(Integer, ForeignKey("candidate_profiles.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("job_descriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    global_score = Column(Numeric(5, 2), index=True)
    semantic_score = Column(Numeric(5, 4))
    skills_score = Column(Numeric(5, 4))
    experience_score = Column(Numeric(5, 4))
    education_score = Column(Numeric(5, 4))
    explanation = Column(Text)
    matched_skills = Column(JSONB, server_default='[]')
    missing_skills = Column(JSONB, server_default='[]')
    scored_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('candidate_profile_id', 'job_id', name='uq_scoring_profile_job'),
    )
