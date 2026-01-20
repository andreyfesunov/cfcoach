from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse

from domain.repositories.codeforces import CodeforcesRepository
from domain.repositories.users import UserRepository
from infrastructure.repositories.sessions import SessionRepository
from domain.models.user import User
from rest.dependencies import (
    get_codeforces_repository,
    get_user_repository,
    get_session_repository,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(
    codeforces_repository: CodeforcesRepository = Depends(get_codeforces_repository),
):
    auth_url = codeforces_repository.get_auth_url()
    return RedirectResponse(url=str(auth_url))


@router.get("/callback")
async def oauth_callback(
    code: str,
    state: str | None = None,
    codeforces_repository: CodeforcesRepository = Depends(get_codeforces_repository),
    user_repository: UserRepository = Depends(get_user_repository),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    try:
        token_response = codeforces_repository.exchange_code_for_tokens(code, state)

        if not token_response or "access_token" not in token_response:
            error_msg = f"Token response missing access_token: {token_response}"
            raise HTTPException(status_code=400, detail=error_msg)

        access_token = token_response["access_token"]
        id_token = token_response.get("id_token")

        user_info = codeforces_repository.get_user_info(access_token, id_token)

        external_user_id = (
            user_info.get("sub") or user_info.get("id") or user_info.get("handle")
        )

        if not external_user_id:
            raise HTTPException(status_code=400, detail="User ID not found in response")

        username = (
            user_info.get("handle")
            or user_info.get("preferred_username")
            or user_info.get("username")
        )

        user = await user_repository.find_by_external_id(external_user_id)

        if not user:
            user = User(
                external_id=external_user_id,
                username=username,
                access_token=access_token,
            )
            user = await user_repository.create(user)
        else:
            if username:
                user.username = username
            user.access_token = access_token
            user = await user_repository.update(user)

        if user.id is None:
            raise HTTPException(status_code=500, detail="User ID is not set")

        session_token = session_repository.create_session(user.id)

        redirect_response = RedirectResponse(url="/")
        redirect_response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )

        return redirect_response

    except HTTPException:
        raise
    except ValueError as e:
        error_msg = str(e)
        if ":" in error_msg and error_msg.split(":")[0].strip().isdigit():
            status_code = int(error_msg.split(":")[0].strip())
            detail = ":".join(error_msg.split(":")[1:]).strip()
            raise HTTPException(status_code=status_code, detail=detail)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")
