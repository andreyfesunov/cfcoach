from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class Submission(BaseModel):
    id: Optional[int] = None
    user_id: int
    submission_id: int
    contest_id: Optional[int] = None
    problem_index: Optional[str] = None
    problem_name: Optional[str] = None
    verdict: str
    programming_language: str
    creation_time_seconds: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
