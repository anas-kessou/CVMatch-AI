import json
import logging
from pydantic import BaseModel, Field
from typing import List, Optional
import google.generativeai as genai
import instructor

logger = logging.getLogger(__name__)

class IdentifiedSkill(BaseModel):
    name: str

class Experience(BaseModel):
    job_title: str
    company: str

class Education(BaseModel):
    degree: str
    field_of_study: str
    institution: str

class CVProfile(BaseModel):
    full_name: str
    email: str
    phone: str
    location: str
    total_experience_years: float = Field(description="Calculate or estimate the total years of professional experience across all jobs.")
    summary: Optional[str] = Field(default=None, description="A brief professional summary of the candidate.")
    hard_skills: List[IdentifiedSkill] = []
    soft_skills: List[IdentifiedSkill] = []
    experiences: List[Experience] = []
    education: List[Education] = []

class ExtractorService:
    def __init__(self):
        # Configure Gemini
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY environment variable is not set. Defaulting to empty.")
            api_key = ""
        genai.configure(api_key=api_key)
        
        # Patch the Gemini client with instructor
        self.client = instructor.from_gemini(
            client=genai.GenerativeModel('models/gemini-1.5-flash'),
            mode=instructor.Mode.GEMINI_JSON,
        )

    # Use tenacity to handle 429 Too Many Requests (Rate limit) from Gemini
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

    @retry(
        stop=stop_after_attempt(5), 
        wait=wait_exponential(multiplier=2, min=4, max=30), 
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def _call_gemini(self, raw_markdown: str):
        return self.client.messages.create(
            messages=[
                {
                    "role": "user",
                    "content": f"Extract the candidate's professional profile from the following CV markdown. Return structured data:\n\n{raw_markdown}",
                }
            ],
            response_model=CVProfile,
        )

    async def extract_cv(self, raw_markdown: str) -> CVProfile:
        logger.info("Extracting CV Profile using Gemini (Instructor) with Rate Limit Handling...")
        try:
            # We call the synchronous rate-limited method inside an async function
            response = self._call_gemini(raw_markdown)
            logger.info(f"Successfully extracted profile for {response.full_name}")
            return response
        except Exception as e:
            logger.error(f"Failed to extract CV with Gemini after retries: {e}")
            # Fallback to empty mock
            return CVProfile(
                full_name="Extraction Failed", 
                email="", 
                phone="", 
                location="", 
                total_experience_years=0.0
            )

extractor_service = ExtractorService()
