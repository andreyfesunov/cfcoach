from pydantic import BaseModel
from typing import Optional, List


class Problem(BaseModel):
    id: Optional[int] = None
    contest_id: Optional[int] = None
    problem_index: Optional[str] = None
    name: str
    problem_type: Optional[str] = None
    points: Optional[float] = None
    rating: Optional[int] = None
    tags: List[str] = []
