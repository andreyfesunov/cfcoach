import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import SecretStr


class SessionRepository:
    def __init__(self, secret_key: SecretStr, algorithm: str = "HS256"):
        self.secret_key = secret_key.get_secret_value()
        self.algorithm = algorithm

    def create_session(self, user_id: int) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_session(self, token: str) -> Optional[int]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload.get("user_id")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_user_id(self, token: str) -> Optional[int]:
        return self.verify_session(token)
