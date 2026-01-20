from dataclasses import dataclass


@dataclass(frozen=True)
class UserAuthenticatedEvent:
    user_id: int
    external_id: str
    username: str | None
    access_token: str
