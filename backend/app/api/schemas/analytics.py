from __future__ import annotations

from pydantic import BaseModel


class RangeBucket(BaseModel):
    range: str
    count: int


class AnalyticsResponse(BaseModel):
    score_distribution: list[RangeBucket]
    status_distribution: list[RangeBucket]
