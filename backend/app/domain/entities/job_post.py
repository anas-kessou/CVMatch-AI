from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class JobPost:
    title: str
    company: str
    description: str
    required_hard_skills: list[str] = field(default_factory=list)
    required_soft_skills: list[str] = field(default_factory=list)
    min_experience: int = 0
    education_level: str = "other"
