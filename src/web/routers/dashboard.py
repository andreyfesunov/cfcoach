from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from domain.models.user import User
from domain.repositories.submissions import SubmissionRepository
from domain.repositories.rating_changes import RatingChangeRepository
from domain.repositories.user_problem_status import UserProblemStatusRepository
from domain.repositories.user_contest_participation import (
    UserContestParticipationRepository,
)
from application.services.recommendation_service import RecommendationService
from web.dependencies import get_current_user
from web.utils import get_template_engine
from rest.dependencies import (
    get_submission_repository,
    get_rating_change_repository,
    get_problem_status_repository,
    get_participation_repository,
    get_recommendation_service,
)

router = APIRouter()
templates = get_template_engine()


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User | None = Depends(get_current_user),
    submission_repository: SubmissionRepository = Depends(get_submission_repository),
    rating_change_repository: RatingChangeRepository = Depends(
        get_rating_change_repository
    ),
    problem_status_repository: UserProblemStatusRepository = Depends(
        get_problem_status_repository
    ),
    participation_repository: UserContestParticipationRepository = Depends(
        get_participation_repository
    ),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
):
    stats = {
        "total_submissions": 0,
        "solved_problems": 0,
        "attempted_problems": 0,
        "contests_participated": 0,
        "current_rating": None,
        "max_rating": None,
    }

    recommendations = []
    rating_history = []

    if current_user and current_user.id:
        submissions = await submission_repository.find_by_user_id(current_user.id)
        stats["total_submissions"] = len(submissions)

        solved_statuses = await problem_status_repository.find_solved_by_user_id(
            current_user.id
        )
        stats["solved_problems"] = len(solved_statuses)

        attempted_statuses = await problem_status_repository.find_by_user_id(
            current_user.id
        )
        stats["attempted_problems"] = len(attempted_statuses)

        participations = await participation_repository.find_by_user_id(current_user.id)
        stats["contests_participated"] = len(
            [p for p in participations if p.participated]
        )

        rating_changes = await rating_change_repository.find_by_user_id(current_user.id)
        if rating_changes:
            rating_history = [
                {"contest_id": rc.contest_id, "new_rating": rc.new_rating}
                for rc in sorted(
                    rating_changes, key=lambda x: x.contest_id or 0, reverse=True
                )[:10]
            ]
            latest = rating_changes[0]
            stats["current_rating"] = latest.new_rating
            stats["max_rating"] = max(
                (rc.new_rating for rc in rating_changes if rc.new_rating), default=None
            )

        recommendations_data = await recommendation_service.get_recommendations(
            current_user.id, limit=3
        )
        recommendations = recommendations_data

    return templates.TemplateResponse(
        "pages/dashboard.html",
        {
            "request": request,
            "current_user": current_user,
            "stats": stats,
            "recommendations": recommendations,
            "rating_history": rating_history,
        },
    )
