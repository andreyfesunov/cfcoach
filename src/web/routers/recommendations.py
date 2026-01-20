from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from typing import Optional

from domain.models.user import User
from domain.repositories.problems import ProblemRepository
from application.services.recommendation_service import RecommendationService
from web.dependencies import require_auth
from web.utils import get_template_engine
from web.services.explanation_service import ExplanationService
from rest.dependencies import (
    get_problem_repository,
    get_recommendation_service,
    get_problem_status_repository,
    get_submission_repository,
    get_user_problem_rating_repository,
)

router = APIRouter()
templates = get_template_engine()


@router.get("/recommendations", response_class=HTMLResponse)
async def recommendations_page(
    request: Request,
    current_user: User = Depends(require_auth),
    recommender_type: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    problem_repository: ProblemRepository = Depends(get_problem_repository),
):
    if current_user.id is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="User ID is not set")

    recommendations_data = await recommendation_service.get_recommendations(
        current_user.id, recommender_type, limit
    )

    available_types = await recommendation_service.get_available_types()

    explanation_service = ExplanationService(
        problem_repository=problem_repository,
        user_problem_status_repository=get_problem_status_repository(),
        submission_repository=get_submission_repository(),
        user_problem_rating_repository=get_user_problem_rating_repository(),
    )

    recommendations_with_explanations = []

    for rec in recommendations_data:
        problem = None
        if rec["contest_id"] and rec["problem_index"]:
            problem = await problem_repository.find_by_contest_and_index(
                rec["contest_id"], rec["problem_index"]
            )

        explanation = await explanation_service.explain_recommendation(
            current_user.id, rec, recommender_type or "content_based"
        )

        recommendations_with_explanations.append(
            {
                "recommendation": rec,
                "problem": problem,
                "explanation": explanation,
            }
        )

    return templates.TemplateResponse(
        "pages/recommendations.html",
        {
            "request": request,
            "current_user": current_user,
            "recommendations": recommendations_with_explanations,
            "available_types": available_types,
            "current_type": recommender_type,
        },
    )
