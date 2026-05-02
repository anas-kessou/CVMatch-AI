import os
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CVFile, CandidateProfile, JobDescription, ScoringResult

# === Services Modernes 2026 ===
from app.core.cv_parser import CVParser
from app.core.extractor_service import extractor_service, CVProfile
from app.core.embedding_engine import embedding_service
from app.core.scoring_service import scoring_service

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./data/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialisation des services
cv_parser = CVParser()


@router.post("/jobs/{job_id}/cvs/upload", tags=["cv"])
async def upload_cv(
    job_id: int, 
    file: UploadFile = File(...), 
    weight_skills: float = Form(0.40),
    weight_experience: float = Form(0.30),
    weight_education: float = Form(0.20),
    weight_soft_skills: float = Form(0.10),
    db: Session = Depends(get_db)
):
    """
    Endpoint moderne d'upload et analyse de CV (Pipeline 2026)
    """
    # 1. Vérification du Job
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 2. Vérification du type de fichier
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ]:
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file type. Only PDF and DOCX are allowed."
        )

    # 3. Lecture et sauvegarde du fichier
    file_bytes = await file.read()
    cv_uuid = str(uuid.uuid4())
    ext = Path(file.filename).suffix.lower()
    out_path = UPLOAD_DIR / f"{cv_uuid}{ext}"

    try:
        with out_path.open("wb") as f:
            f.write(file_bytes)

        logger.info(f"CV uploaded: {file.filename} → {out_path}")

        # ====================== PIPELINE COMPLET 2026 ======================
        
        # Parsing avec Docling 2.x
        raw_markdown = cv_parser.parse_cv(file_bytes, file.filename)

        # Extraction structurée (Instructor)
        cv_profile: CVProfile = await extractor_service.extract_cv(raw_markdown)

        # Embedding avec BAAI/bge-m3
        embedding_result = embedding_service.get_multi_embeddings(raw_markdown)
        dense_vector = embedding_result["dense"]

        # ====================== SAUVEGARDE EN BASE ======================
        
        # CV File
        db_cv = CVFile(
            job_id=job.id,
            original_filename=file.filename,
            stored_path=str(out_path),
            file_type="pdf" if ext == ".pdf" else "docx",
            file_size_bytes=len(file_bytes),
            status="processing"
        )
        db.add(db_cv)
        db.flush()
        db.refresh(db_cv)

        # Candidate Profile
        profile = CandidateProfile(
            cv_file_id=db_cv.id,
            full_name=cv_profile.full_name,
            email=cv_profile.email,
            phone=cv_profile.phone,
            location=cv_profile.location,
            total_experience_years=getattr(cv_profile, 'total_experience_years', 0.0),
            summary_text=cv_profile.summary[:1000] if cv_profile.summary else "",
            raw_text=raw_markdown,
            embedding_vector=dense_vector
        )
        db.add(profile)
        db.flush()
        db.refresh(profile)

        # ====================== SCORING ======================
        weights = {
            "skills": weight_skills,
            "experience": weight_experience,
            "education": weight_education,
            "soft_skills": weight_soft_skills
        }
        score_result = await scoring_service.score_candidate(cv_profile, job.description, weights)

        # Scoring Result
        scoring = ScoringResult(
            candidate_profile_id=profile.id,
            job_id=job.id,
            global_score=score_result["global_score"],
            semantic_score=score_result.get("semantic_score", 0),
            skills_score=score_result.get("skills_score", 0),
            experience_score=score_result.get("experience_score", 0),
            education_score=score_result.get("education_score", 0),
            explanation=score_result.get("overall_assessment", ""),
            # Tu peux ajouter plus de champs selon ton modèle ScoringResult
        )
        db.add(scoring)

        # Mise à jour du statut
        db_cv.status = "scored"
        db.commit()

        logger.info(f"CV {db_cv.id} processed successfully with score: {score_result['global_score']}")

        return {
            "message": "CV processed successfully",
            "cv_id": db_cv.id,
            "candidate_name": cv_profile.full_name,
            "global_score": score_result["global_score"],
            "recommendation": score_result.get("interview_recommendation", "maybe")
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Error processing CV {file.filename}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")