from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserProblemRating(BaseModel):
    id: Optional[int] = None
    user_id: int
    contest_id: Optional[int] = None
    problem_index: Optional[str] = None
    difficulty_rating: Optional[int] = None
    usefulness_rating: Optional[int] = None
    interest_rating: Optional[int] = None
    quality_rating: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
