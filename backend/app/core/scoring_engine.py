from app.core.embedding_engine import get_embedding
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def score_candidate(candidate_text: str, job_description_text: str) -> dict:
    c_emb = np.array(get_embedding(candidate_text)).reshape(1, -1)
    j_emb = np.array(get_embedding(job_description_text)).reshape(1, -1)
    
    sem_score = cosine_similarity(c_emb, j_emb)[0][0]
    
    # Placeholder for full hybrid logic
    global_score = float(sem_score * 100)
    
    return {
        "global_score": min(max(global_score, 0), 100),
        "semantic_score": float(sem_score),
        "skills_score": 0.8,
        "experience_score": 1.0,
        "education_score": 1.0,
        "matched_skills": [],
        "missing_skills": [],
        "explanation": "Scoring explanation..."
    }
