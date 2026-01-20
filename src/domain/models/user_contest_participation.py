from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserContestParticipation(BaseModel):
    id: Optional[int] = None
    user_id: int
    contest_id: int
    participated: bool
    first_submission_time: Optional[int] = None
    last_submission_time: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
