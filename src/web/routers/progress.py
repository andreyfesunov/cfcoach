from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from domain.models.user import User
from domain.repositories.rating_changes import RatingChangeRepository
from domain.repositories.user_problem_status import UserProblemStatusRepository
from domain.repositories.submissions import SubmissionRepository
from web.dependencies import require_auth
from web.utils import get_template_engine
from rest.dependencies import (
    get_rating_change_repository,
    get_problem_status_repository,
    get_submission_repository,
)

router = APIRouter()
templates = get_template_engine()


@router.get("/progress", response_class=HTMLResponse)
async def progress_page(
    request: Request,
    current_user: User = Depends(require_auth),
    rating_change_repository: RatingChangeRepository = Depends(
        get_rating_change_repository
    ),
    problem_status_repository: UserProblemStatusRepository = Depends(
        get_problem_status_repository
    ),
    submission_repository: SubmissionRepository = Depends(get_submission_repository),
):
    if current_user.id is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="User ID is not set")

    rating_changes = await rating_change_repository.find_by_user_id(current_user.id)
    solved_statuses = await problem_status_repository.find_solved_by_user_id(
        current_user.id
    )
    submissions = await submission_repository.find_by_user_id(current_user.id)

    rating_history = [
        {
            "time": rc.rating_update_time_seconds,
            "rating": rc.new_rating,
            "contest_name": rc.contest_name,
        }
        for rc in sorted(
            rating_changes, key=lambda x: x.rating_update_time_seconds, reverse=False
        )
    ]

    solved_by_time: dict[int, int] = {}
    for status in solved_statuses:
        if status.first_solved_time:
            time_key = status.first_solved_time // (86400 * 7)
            solved_by_time[time_key] = solved_by_time.get(time_key, 0) + 1

    solved_timeline = [
        {"week": week, "count": count} for week, count in sorted(solved_by_time.items())
    ]

    tag_distribution: dict[str, int] = {}

    difficulty_distribution: dict[str, int] = {"easy": 0, "medium": 0, "hard": 0}

    return templates.TemplateResponse(
        "pages/progress.html",
        {
            "request": request,
            "current_user": current_user,
            "rating_history": rating_history,
            "solved_timeline": solved_timeline,
            "tag_distribution": tag_distribution,
            "difficulty_distribution": difficulty_distribution,
            "total_solved": len(solved_statuses),
            "total_submissions": len(submissions),
        },
    )
