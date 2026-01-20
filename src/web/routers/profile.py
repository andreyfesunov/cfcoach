from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from domain.models.user import User
from domain.repositories.submissions import SubmissionRepository
from domain.repositories.rating_changes import RatingChangeRepository
from domain.repositories.user_problem_status import UserProblemStatusRepository
from domain.repositories.user_contest_participation import (
    UserContestParticipationRepository,
)
from web.dependencies import require_auth
from web.utils import get_template_engine
from rest.dependencies import (
    get_submission_repository,
    get_rating_change_repository,
    get_problem_status_repository,
    get_participation_repository,
)

router = APIRouter()
templates = get_template_engine()


@router.get("/profile", response_class=HTMLResponse)
async def profile(
    request: Request,
    current_user: User = Depends(require_auth),
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
):
    if current_user.id is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="User ID is not set")

    submissions = await submission_repository.find_by_user_id(current_user.id)
    solved_statuses = await problem_status_repository.find_solved_by_user_id(
        current_user.id
    )
    attempted_statuses = await problem_status_repository.find_by_user_id(
        current_user.id
    )
    participations = await participation_repository.find_by_user_id(current_user.id)
    rating_changes = await rating_change_repository.find_by_user_id(current_user.id)

    rating_history = [
        {
            "contest_id": rc.contest_id,
            "contest_name": rc.contest_name,
            "old_rating": rc.old_rating,
            "new_rating": rc.new_rating,
            "rank": rc.rank,
        }
        for rc in sorted(
            rating_changes, key=lambda x: x.rating_update_time_seconds, reverse=True
        )
    ]

    tag_stats: dict[str, int] = {}

    return templates.TemplateResponse(
        "pages/profile.html",
        {
            "request": request,
            "current_user": current_user,
            "submissions": submissions[:20],
            "solved_count": len(solved_statuses),
            "attempted_count": len(attempted_statuses),
            "participations_count": len([p for p in participations if p.participated]),
            "rating_history": rating_history,
            "tag_stats": tag_stats,
        },
    )
