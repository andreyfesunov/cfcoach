from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from typing import Any

from domain.models.user import User
from domain.repositories.users import UserRepository
from domain.repositories.user_problem_status import UserProblemStatusRepository
from web.dependencies import require_auth
from web.utils import get_template_engine
from rest.dependencies import (
    get_user_repository,
    get_problem_status_repository,
)

router = APIRouter()
templates = get_template_engine()


@router.get("/comparison", response_class=HTMLResponse)
async def comparison_page(
    request: Request,
    current_user: User = Depends(require_auth),
    user_repository: UserRepository = Depends(get_user_repository),
    problem_status_repository: UserProblemStatusRepository = Depends(
        get_problem_status_repository
    ),
):
    if current_user.id is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="User ID is not set")

    all_users = await user_repository.find_all()

    current_solved = await problem_status_repository.find_solved_by_user_id(
        current_user.id
    )
    current_solved_set = {
        (s.contest_id, s.problem_index)
        for s in current_solved
        if s.contest_id and s.problem_index
    }

    similar_users = []

    for user in all_users:
        if user.id is None or user.id == current_user.id:
            continue

        user_solved = await problem_status_repository.find_solved_by_user_id(user.id)
        user_solved_set = {
            (s.contest_id, s.problem_index)
            for s in user_solved
            if s.contest_id and s.problem_index
        }

        intersection = current_solved_set & user_solved_set
        union = current_solved_set | user_solved_set

        similarity = len(intersection) / len(union) if union else 0.0

        if similarity > 0.1:
            only_other = user_solved_set - current_solved_set
            only_current = current_solved_set - user_solved_set

            similar_users.append(
                {
                    "user": user,
                    "similarity": similarity,
                    "common_problems": len(intersection),
                    "only_other_count": len(only_other),
                    "only_current_count": len(only_current),
                }
            )

    def get_similarity(item: dict[str, Any]) -> float:
        return float(item["similarity"])

    similar_users.sort(key=get_similarity, reverse=True)

    return templates.TemplateResponse(
        "pages/comparison.html",
        {
            "request": request,
            "current_user": current_user,
            "similar_users": similar_users[:10],
        },
    )
