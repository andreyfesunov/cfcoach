from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse

from domain.models.user import User
from application.services.recommendation_service import RecommendationService
from web.dependencies import require_auth
from web.utils import get_template_engine
from rest.dependencies import get_recommendation_service

router = APIRouter()
templates = get_template_engine()


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_user: User = Depends(require_auth),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
):
    available_types = await recommendation_service.get_available_types()

    from rest.dependencies import get_user_preferences_repository

    preferences_repo = get_user_preferences_repository()
    preferences = None
    if current_user.id:
        preferences = await preferences_repo.find_by_user_id(current_user.id)

    current_type = (
        preferences.preferred_recommender_type if preferences else "content_based"
    )

    return templates.TemplateResponse(
        "pages/settings.html",
        {
            "request": request,
            "current_user": current_user,
            "available_types": available_types,
            "current_type": current_type,
        },
    )


@router.post("/settings", response_class=HTMLResponse)
async def update_settings(
    request: Request,
    current_user: User = Depends(require_auth),
    recommender_type: str = Form(...),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
):
    if current_user.id is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="User ID is not set")

    try:
        await recommendation_service.set_user_preference(
            current_user.id, recommender_type
        )
        return RedirectResponse(url="/settings", status_code=303)
    except ValueError as e:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=str(e))
