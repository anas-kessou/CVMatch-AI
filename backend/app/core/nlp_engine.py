import re

def extract_entities(text: str) -> dict:
    """
    Dummy standard implementation for NER until spacy is fully loaded.
    """
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text)
    phone_match = re.search(r"(\+?\d{1,3}[\s-]?\d{8,12})", text)
    
    return {
        "email": email_match.group(0) if email_match else "",
        "phone": phone_match.group(0) if phone_match else "",
        "skills": ["python", "machine learning"], # Placeholder for matching
        "total_experience_years": 3,
        "education_level": "Master",
    }
