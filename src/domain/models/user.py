from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class User(BaseModel):
    id: Optional[int] = None
    external_id: Optional[str] = None
    username: Optional[str] = None
    access_token: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
