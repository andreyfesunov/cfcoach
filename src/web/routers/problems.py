from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from typing import Optional

from domain.models.user import User
from domain.repositories.problems import ProblemRepository
from domain.repositories.user_problem_status import UserProblemStatusRepository
from web.dependencies import get_current_user
from web.utils import get_template_engine
from rest.dependencies import (
    get_problem_repository,
    get_problem_status_repository,
)

router = APIRouter()
templates = get_template_engine()


@router.get("/problems", response_class=HTMLResponse)
async def problems_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    min_rating: Optional[int] = Query(None),
    max_rating: Optional[int] = Query(None),
    tag: Optional[str] = Query(None),
    contest_id: Optional[int] = Query(None),
    problem_repository: ProblemRepository = Depends(get_problem_repository),
    problem_status_repository: UserProblemStatusRepository = Depends(
        get_problem_status_repository
    ),
):
    all_problems = []

    if contest_id:
        problems = await problem_repository.find_by_contest_id(contest_id)
        all_problems = problems
    else:
        from rest.dependencies import get_contest_repository

        contest_repo = get_contest_repository()
        contests = await contest_repo.find_all()

        for contest in contests:
            problems = await problem_repository.find_by_contest_id(contest.contest_id)
            all_problems.extend(problems)

    filtered_problems = []

    for problem in all_problems:
        if min_rating and problem.rating and problem.rating < min_rating:
            continue
        if max_rating and problem.rating and problem.rating > max_rating:
            continue
        if tag and problem.tags and tag not in problem.tags:
            continue
        filtered_problems.append(problem)

    solved_problems = set()
    if current_user and current_user.id:
        solved_statuses = await problem_status_repository.find_solved_by_user_id(
            current_user.id
        )
        solved_problems = {
            (s.contest_id, s.problem_index)
            for s in solved_statuses
            if s.contest_id and s.problem_index
        }

    return templates.TemplateResponse(
        "pages/problems.html",
        {
            "request": request,
            "current_user": current_user,
            "problems": filtered_problems[:100],
            "solved_problems": solved_problems,
            "min_rating": min_rating,
            "max_rating": max_rating,
            "tag": tag,
            "contest_id": contest_id,
        },
    )
