from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserPreferences(BaseModel):
    id: Optional[int] = None
    user_id: int
    preferred_recommender_type: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
