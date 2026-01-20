from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional

from domain.models.user import User
from domain.repositories.problems import ProblemRepository
from domain.repositories.user_problem_rating import UserProblemRatingRepository
from domain.models.user_problem_rating import UserProblemRating
from web.dependencies import require_auth
from web.utils import get_template_engine
from rest.dependencies import (
    get_problem_repository,
    get_user_problem_rating_repository,
)

router = APIRouter()
templates = get_template_engine()


@router.get("/problems/{contest_id}/{problem_index}/rate", response_class=HTMLResponse)
async def rate_page(
    request: Request,
    contest_id: int,
    problem_index: str,
    current_user: User = Depends(require_auth),
    problem_repository: ProblemRepository = Depends(get_problem_repository),
    rating_repository: UserProblemRatingRepository = Depends(
        get_user_problem_rating_repository
    ),
):
    if current_user.id is None:
        raise HTTPException(status_code=400, detail="User ID is not set")

    problem = await problem_repository.find_by_contest_and_index(
        contest_id, problem_index
    )

    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    existing_rating = await rating_repository.find_by_user_and_problem(
        current_user.id, contest_id, problem_index
    )

    all_ratings = await rating_repository.find_by_problem(contest_id, problem_index)

    avg_difficulty = 0.0
    avg_usefulness = 0.0
    avg_interest = 0.0
    avg_quality = 0.0
    count = 0

    for rating in all_ratings:
        if rating.difficulty_rating:
            avg_difficulty += rating.difficulty_rating
        if rating.usefulness_rating:
            avg_usefulness += rating.usefulness_rating
        if rating.interest_rating:
            avg_interest += rating.interest_rating
        if rating.quality_rating:
            avg_quality += rating.quality_rating
        count += 1

    if count > 0:
        avg_difficulty /= count
        avg_usefulness /= count
        avg_interest /= count
        avg_quality /= count

    return templates.TemplateResponse(
        "pages/rate.html",
        {
            "request": request,
            "current_user": current_user,
            "problem": problem,
            "existing_rating": existing_rating,
            "avg_difficulty": avg_difficulty,
            "avg_usefulness": avg_usefulness,
            "avg_interest": avg_interest,
            "avg_quality": avg_quality,
            "ratings_count": count,
        },
    )


@router.post("/problems/{contest_id}/{problem_index}/rate", response_class=HTMLResponse)
async def submit_rating(
    request: Request,
    contest_id: int,
    problem_index: str,
    current_user: User = Depends(require_auth),
    difficulty_rating: Optional[int] = Form(None),
    usefulness_rating: Optional[int] = Form(None),
    interest_rating: Optional[int] = Form(None),
    quality_rating: Optional[int] = Form(None),
    rating_repository: UserProblemRatingRepository = Depends(
        get_user_problem_rating_repository
    ),
):
    if current_user.id is None:
        raise HTTPException(status_code=400, detail="User ID is not set")

    existing = await rating_repository.find_by_user_and_problem(
        current_user.id, contest_id, problem_index
    )

    if existing:
        existing.difficulty_rating = difficulty_rating
        existing.usefulness_rating = usefulness_rating
        existing.interest_rating = interest_rating
        existing.quality_rating = quality_rating
        await rating_repository.update(existing)
    else:
        new_rating = UserProblemRating(
            user_id=current_user.id,
            contest_id=contest_id,
            problem_index=problem_index,
            difficulty_rating=difficulty_rating,
            usefulness_rating=usefulness_rating,
            interest_rating=interest_rating,
            quality_rating=quality_rating,
        )
        await rating_repository.create(new_rating)

    return RedirectResponse(
        url=f"/problems/{contest_id}/{problem_index}/rate", status_code=303
    )
