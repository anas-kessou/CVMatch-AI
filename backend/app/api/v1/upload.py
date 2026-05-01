import os
import uuid
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import CVFile, CandidateProfile, JobDescription, ScoringResult
from app.core.cv_parser import parse_cv
from app.core.nlp_engine import extract_entities
from app.core.embedding_engine import get_embedding
from app.core.scoring_engine import score_candidate

router = APIRouter()

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./data/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/jobs/{job_id}/cvs/upload", tags=["cv"])
async def upload_cv(job_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    job = db.query(JobDescription).filter(JobDescription.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if file.content_type not in (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ):
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or DOCX.")

    file_bytes = await file.read()
    
    cv_uuid = str(uuid.uuid4())
    ext = Path(file.filename).suffix or ""
    out_path = UPLOAD_DIR / f"{cv_uuid}{ext}"

    with out_path.open("wb") as f:
        f.write(file_bytes)
        
    db_cv = CVFile(
        job_id=job.id,
        original_filename=file.filename,
        stored_path=str(out_path),
        file_type="pdf" if ext.lower() == ".pdf" else "docx",
        file_size_bytes=len(file_bytes),
        status="processing"
    )
    db.add(db_cv)
    db.flush()
    db.refresh(db_cv)

    # Extraction pipeline
    raw_text = parse_cv(file_bytes, file.filename)
    structured_data = extract_entities(raw_text)
    
    cv_vector = get_embedding(raw_text)
    
    profile = CandidateProfile(
        cv_file_id=db_cv.id,
        full_name=structured_data.get("email"), # Mocked fallback
        email=structured_data.get("email"),
        phone=structured_data.get("phone"),
        total_experience_years=structured_data.get("total_experience_years"),
        summary_text=raw_text[:500],
        raw_text=raw_text,
        embedding_vector=cv_vector
    )
    db.add(profile)
    db.flush()
    db.refresh(profile)

    # Scoring pipeline
    score_res = score_candidate(raw_text, job.description)
    
    scoring = ScoringResult(
        candidate_profile_id=profile.id,
        job_id=job.id,
        global_score=score_res["global_score"],
        semantic_score=score_res["semantic_score"],
        skills_score=score_res["skills_score"],
        experience_score=score_res["experience_score"],
        education_score=score_res["education_score"],
        explanation=score_res["explanation"]
    )
    db.add(scoring)
    
    db_cv.status = "scored"
    db.commit()

    return {"message": "CV processed successfully", "cv_id": db_cv.id, "score": score_res["global_score"]}
