from fastapi import Request, HTTPException, Depends
from typing import Optional

from domain.models.user import User
from domain.repositories.users import UserRepository
from infrastructure.repositories.sessions import SessionRepository
from rest.dependencies import get_user_repository, get_session_repository


async def get_current_user(
    request: Request,
    user_repository: UserRepository = Depends(get_user_repository),
    session_repository: SessionRepository = Depends(get_session_repository),
) -> Optional[User]:
    session_token = request.cookies.get("session_token")

    if not session_token:
        return None

    user_id = session_repository.verify_session(session_token)

    if user_id is None:
        return None

    return await user_repository.find_by_id(user_id)


async def require_auth(
    current_user: Optional[User] = Depends(get_current_user),
) -> User:
    if current_user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user
