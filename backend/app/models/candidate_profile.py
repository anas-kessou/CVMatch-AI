from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Numeric
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database import Base

class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    cv_file_id = Column(Integer, ForeignKey("cv_files.id", ondelete="CASCADE"), nullable=False, unique=True)
    full_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    total_experience_years = Column(Numeric(4, 1), nullable=True)
    raw_text = Column(Text, nullable=True)
    summary_text = Column(Text, nullable=True)
    embedding_vector = Column(Vector(768), nullable=True)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())
