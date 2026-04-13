from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Candidate:
    id: int | None
    name: str
    email: str | None
    raw_text: str = ""
    hard_skills: list[str] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    experience_years: int | None = None
    education_level: str | None = None
