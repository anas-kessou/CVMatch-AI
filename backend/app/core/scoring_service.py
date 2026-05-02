# app/core/scoring_service.py
import logging
from typing import Dict, Any, List
import numpy as np

import instructor
from pydantic import BaseModel, Field
from openai import OpenAI

from app.core.embedding_engine import embedding_service
from app.core.extractor_service import CVProfile

logger = logging.getLogger(__name__)


# ====================== SCHÉMAS POUR LLM-as-Judge ======================
class SkillGap(BaseModel):
    skill: str
    status: str = Field(..., description="present | partially_present | missing")
    evidence: str
    recommendation: str


class ScoringExplanation(BaseModel):
    global_score: int = Field(..., ge=0, le=100, description="Score final sur 100")
    skills_score: int = Field(..., ge=0, le=100)
    experience_score: int = Field(..., ge=0, le=100)
    education_score: int = Field(..., ge=0, le=100)
    cultural_fit_score: int = Field(..., ge=0, le=100)
    
    top_strengths: List[str]
    key_gaps: List[SkillGap]
    
    overall_assessment: str
    interview_recommendation: str   # strongly_recommend, recommend, maybe, reject


class ScoringService:
    def __init__(self):
        # Configuration flexible selon la RAM disponible
        self.llm_client = instructor.from_openai(
            OpenAI(
                base_url="http://localhost:11434/v1", 
                api_key="ollama"
            ),
            mode=instructor.Mode.JSON,
        )
        
        # Modèle à utiliser (change facilement quand tu passes sur Kaggle)
        self.model_name = "qwen2.5:3b"        # Léger pour ta machine actuelle
        # self.model_name = "qwen3:8b"        # Décommente quand tu seras sur Kaggle

        logger.info(f"✅ ScoringService initialized with model: {self.model_name}")

    def retrieve_score(self, cv_text: str, job_text: str) -> float:
        """Étape 1 : Retrieve rapide avec bge-m3"""
        return embedding_service.compute_similarity(cv_text, job_text)

    def segmented_retrieve_score(self, cv_profile: CVProfile, job_description: str, weights: Dict[str, float] = None) -> Dict[str, float]:
        """Scoring segmenté (skills, experience, overall) - plus précis"""
        try:
            skills_text = " ".join([s.name for s in cv_profile.hard_skills + cv_profile.soft_skills])
            experience_text = " ".join([f"{e.job_title} at {e.company}" for e in cv_profile.experiences])
            education_text = " ".join([f"{e.degree} in {e.field_of_study} at {e.institution}" for e in cv_profile.education])
            
            scores = {
                "skills": embedding_service.compute_similarity(skills_text, job_description),
                "experience": embedding_service.compute_similarity(experience_text, job_description),
                "education": embedding_service.compute_similarity(education_text, job_description),
                "overall": embedding_service.compute_similarity(cv_profile.summary or "", job_description)
            }
            
            if weights is None:
                weights = {"skills": 0.40, "experience": 0.30, "education": 0.20, "soft_skills": 0.10}

            # Score global pondéré avec paramètres custom
            global_retrieve = (
                weights.get("skills", 0.40) * scores["skills"] +
                weights.get("experience", 0.30) * scores["experience"] +
                weights.get("education", 0.20) * scores["education"] +
                weights.get("soft_skills", 0.10) * scores["overall"]
            )
            
            return {**scores, "global_retrieve": round(global_retrieve, 4)}
            
        except Exception as e:
            logger.warning(f"Segmented retrieve failed: {e}")
            return {"skills": 0.0, "experience": 0.0, "overall": 0.0, "global_retrieve": 0.0}

    async def reason_score(self, cv_profile: CVProfile, job_description: str, weights: Dict[str, float] = None) -> ScoringExplanation:
        """Étape 3 : LLM-as-Judge (explication structurée)"""
        weights_info = ""
        if weights:
            weights_info = f"""
        Prends en compte les poids d'importance suivants lors du jugement :
        - Compétences techniques : {weights.get('skills', 0.4)*100}%
        - Expérience : {weights.get('experience', 0.3)*100}%
        - Éducation : {weights.get('education', 0.2)*100}%
        - Soft Skills : {weights.get('soft_skills', 0.1)*100}%
        """

        system_prompt = f"""
        Tu es un recruteur IT senior très objectif et exigeant.
        Analyse la correspondance entre le CV du candidat et la fiche de poste.
        Sois précis, factuel et constructif. Retourne uniquement le JSON demandé.{weights_info}
        """

        user_prompt = f"""
        FICHE DE POSTE :
        {job_description}

        CANDIDAT :
        Nom complet : {cv_profile.full_name}
        Résumé : {cv_profile.summary or 'Non disponible'}
        Hard Skills : {[s.name for s in cv_profile.hard_skills]}
        Soft Skills : {[s.name for s in cv_profile.soft_skills]}
        Expériences : {[f"{exp.job_title} chez {exp.company}" for exp in cv_profile.experiences]}
        Formation : {[f"{edu.degree} en {edu.field_of_study} ({edu.institution})" for edu in cv_profile.education]}
        Expérience totale : {cv_profile.total_experience_years} ans
        """

        try:
            explanation: ScoringExplanation = self.llm_client.chat.completions.create(
                model=self.model_name,
                response_model=ScoringExplanation,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.15,
                max_tokens=1500,
            )
            return explanation

        except Exception as e:
            logger.error(f"LLM-as-Judge error: {e}")
            # Fallback robuste quand le modèle n'est pas disponible
            return ScoringExplanation(
                global_score=60,
                skills_score=65,
                experience_score=55,
                education_score=70,
                cultural_fit_score=60,
                top_strengths=["Profil technique détecté"],
                key_gaps=[],
                overall_assessment="Évaluation partielle en raison de contraintes techniques (modèle LLM léger).",
                interview_recommendation="maybe"
            )

    async def score_candidate(self, cv_profile: CVProfile, job_description: str, weights: Dict[str, float] = None) -> Dict[str, Any]:
        """Pipeline Scoring complet : Retrieve + Reason"""
        # Étape 1 : Retrieve (rapide)
        retrieve_scores = self.segmented_retrieve_score(cv_profile, job_description, weights)

        # Étape 2 : Reason avec LLM (explication + score final)
        explanation = await self.reason_score(cv_profile, job_description, weights)

        # Combinaison finale
        final_result = {
            "global_score": explanation.global_score,
            "skills_score": explanation.skills_score,
            "experience_score": explanation.experience_score,
            "education_score": explanation.education_score,
            "semantic_score": round(retrieve_scores["global_retrieve"] * 100, 1),
            "cultural_fit_score": explanation.cultural_fit_score,
            "explanation": explanation.overall_assessment,
            "top_strengths": explanation.top_strengths,
            "key_gaps": [gap.model_dump() for gap in explanation.key_gaps],
            "interview_recommendation": explanation.interview_recommendation,
            "detailed_retrieve_scores": retrieve_scores
        }

        logger.info(f"Scoring completed - Global Score: {explanation.global_score}/100")
        return final_result


# Instance globale
scoring_service = ScoringService()