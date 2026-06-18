import json
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SBERT_MODEL = "BAAI/bge-m3"

# Known model dimensions to avoid loading just to check size
_MODEL_DIMENSIONS = {
    "BAAI/bge-m3": 1024,
    "sentence-transformers/all-MiniLM-L6-v2": 384,
    "all-MiniLM-L6-v2": 384,
    "sentence-transformers/all-mpnet-base-v2": 768,
    "all-mpnet-base-v2": 768,
}


def _get_default_vector_size() -> int:
    """Determine the vector size from the configured SBERT model."""
    model_name = os.getenv("SBERT_MODEL", DEFAULT_SBERT_MODEL)
    return _MODEL_DIMENSIONS.get(model_name, 1024)


VECTOR_SIZE = _get_default_vector_size()


class EmbeddingService:
    """Create dense vectors from CV JSON and job text using SBERT."""

    def __init__(self):
        self.model = None
        self.model_name = os.getenv("SBERT_MODEL", DEFAULT_SBERT_MODEL)
        self.vector_size = VECTOR_SIZE
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)
            dim = None
            if hasattr(self.model, 'get_embedding_dimension'):
                dim = self.model.get_embedding_dimension()
            elif hasattr(self.model, 'get_sentence_embedding_dimension'):
                dim = self.model.get_sentence_embedding_dimension()
            self.vector_size = int(dim or VECTOR_SIZE)
            # Update module-level VECTOR_SIZE so DB models pick it up
            import app.core.embedding_engine as _self_module
            _self_module.VECTOR_SIZE = self.vector_size
        except Exception as exc:
            print(f"WARNING: SBERT model is not available: {exc}")

def profile_to_text(profile) -> str:
    """Group all profile fields into a single text block for embedding."""
    if not profile:
        return ""

    # Check if we can call flat_skills
    if hasattr(profile, "flat_skills"):
        skills = ", ".join(profile.flat_skills)
    else:
        if hasattr(profile, "model_dump"):
            p_dict = profile.model_dump()
        elif hasattr(profile, "dict"):
            p_dict = profile.dict()
        elif isinstance(profile, dict):
            p_dict = profile
        else:
            p_dict = {}
        
        skills_val = p_dict.get("skills") or {}
        if isinstance(skills_val, dict):
            names: list[str] = []
            for values in skills_val.values():
                if isinstance(values, list):
                    for skill in values:
                        if isinstance(skill, dict):
                            names.append(skill.get("name") or "")
                        elif hasattr(skill, "name"):
                            names.append(getattr(skill, "name", "") or "")
                        else:
                            names.append(str(skill))
            skills = ", ".join(name for name in names if name)
        elif isinstance(skills_val, list):
            skills = ", ".join(str(s) for s in skills_val)
        else:
            skills = str(skills_val)

    if hasattr(profile, "model_dump"):
        p_dict = profile.model_dump()
    elif hasattr(profile, "dict"):
        p_dict = profile.dict()
    elif isinstance(profile, dict):
        p_dict = profile
    else:
        p_dict = {}

    edu_list = p_dict.get("education") or []
    edu_strs = []
    if isinstance(edu_list, list):
        for edu in edu_list:
            if isinstance(edu, dict):
                degree = edu.get("degree") or ""
                school = edu.get("institution") or edu.get("school") or ""
                year = edu.get("year") or edu.get("graduation_year") or ""
                edu_strs.append(f"{degree} {school} {year}".strip())
            elif hasattr(edu, "degree"):
                degree = getattr(edu, "degree", "") or ""
                school = getattr(edu, "institution", "") or getattr(edu, "school", "") or ""
                year = getattr(edu, "year", "") or getattr(edu, "graduation_year", "") or ""
                edu_strs.append(f"{degree} {school} {year}".strip())
            else:
                edu_strs.append(str(edu))
    education = " ".join(edu_strs)

    exp_list = p_dict.get("experience") or []
    exp_strs = []
    if isinstance(exp_list, list):
        for exp in exp_list:
            if isinstance(exp, dict):
                role = exp.get("role") or exp.get("title") or ""
                company = exp.get("company") or ""
                desc = exp.get("description") or ""
                if isinstance(desc, list):
                    desc_str = " ".join(str(d) for d in desc)
                else:
                    desc_str = str(desc)
                exp_strs.append(f"{role} {company} {desc_str}".strip())
            elif hasattr(exp, "role") or hasattr(exp, "title"):
                role = getattr(exp, "role", "") or getattr(exp, "title", "") or ""
                company = getattr(exp, "company", "") or ""
                desc = getattr(exp, "description", "") or ""
                if isinstance(desc, list):
                    desc_str = " ".join(str(d) for d in desc)
                else:
                    desc_str = str(desc)
                exp_strs.append(f"{role} {company} {desc_str}".strip())
            else:
                exp_strs.append(str(exp))
    experience = " ".join(exp_strs)

    lang_list = p_dict.get("languages") or []
    if isinstance(lang_list, list):
        languages = ", ".join(str(l) for l in lang_list)
    else:
        languages = str(lang_list)

    summary = p_dict.get("summary") or ""
    raw_text = p_dict.get("raw_text") or ""

    return (
        f"Skills: {skills}\n"
        f"Experience: {experience}\n"
        f"Education: {education}\n"
        f"Languages: {languages}\n"
        f"Summary: {summary}\n"
        f"Raw CV: {raw_text}"
    )


    def get_embedding_from_profile(self, profile) -> list[float]:
        """Create a dense vector from the extracted CV profile using grouped text."""
        grouped_text = profile_to_text(profile)
        return self._encode(grouped_text)

    def get_embedding_from_json(self, profile_json: dict) -> list[float]:
        """Create a dense vector from the extracted JSON profile."""
        json_str = json.dumps(profile_json, ensure_ascii=False)
        return self._encode(json_str)

    def get_embedding(self, text: str) -> list[float]:
        """Create a dense vector from plain text (used for job descriptions)."""
        return self._encode(text)

    def _encode(self, text: str) -> list[float]:
        if not text:
            return [0.0] * self.vector_size

        if self.model:
            vector = self.model.encode(text, normalize_embeddings=True)
            return vector.tolist()

        return [0.0] * self.vector_size


embedding_service = EmbeddingService()


def get_embedding(text: str) -> list[float]:
    return embedding_service.get_embedding(text)
