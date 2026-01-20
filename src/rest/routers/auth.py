from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse

from domain.repositories.codeforces import CodeforcesRepository
from infrastructure.repositories.sessions import SessionRepository
from application.usecases.authenticate_user import AuthenticateUserUseCase
from rest.dependencies import (
    get_codeforces_repository,
    get_authenticate_user_usecase,
    get_session_repository,
)


router = APIRouter(prefix="/api/auth", tags=["auth"])


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
    authenticate_usecase: AuthenticateUserUseCase = Depends(
        get_authenticate_user_usecase
    ),
    session_repository: SessionRepository = Depends(get_session_repository),
):
    try:
        user = await authenticate_usecase.execute(code, state)

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
