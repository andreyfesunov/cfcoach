from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserProblemStatus(BaseModel):
    id: Optional[int] = None
    user_id: int
    contest_id: Optional[int] = None
    problem_index: Optional[str] = None
    solved: bool
    attempts_count: int
    first_solved_time: Optional[int] = None
    last_attempt_time: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
