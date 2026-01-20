from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RatingChange(BaseModel):
    id: Optional[int] = None
    user_id: int
    contest_id: int
    contest_name: str
    handle: str
    rank: int
    rating_update_time_seconds: int
    old_rating: int
    new_rating: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
