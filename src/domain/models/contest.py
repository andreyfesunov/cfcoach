from pydantic import BaseModel
from typing import Optional


class Contest(BaseModel):
    id: Optional[int] = None
    contest_id: int
    name: str
    contest_type: Optional[str] = None
    phase: Optional[str] = None
    frozen: Optional[bool] = None
    duration_seconds: Optional[int] = None
    start_time_seconds: Optional[int] = None
    relative_time_seconds: Optional[int] = None
    prepared_by: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[int] = None
    kind: Optional[str] = None
    icpc_region: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    season: Optional[str] = None
