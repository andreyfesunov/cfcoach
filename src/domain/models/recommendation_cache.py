from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RecommendationCache(BaseModel):
    id: Optional[int] = None
    user_id: int
    recommender_type: str
    problem_ids: list[int]
    scores: list[float]
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
