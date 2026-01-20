from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import Optional
from pydantic import BaseModel

from domain.repositories.user_problem_rating import UserProblemRatingRepository
from domain.models.user_problem_rating import UserProblemRating
from application.services.recommendation_service import RecommendationService
from infrastructure.repositories.sessions import SessionRepository
from rest.dependencies import (
    get_recommendation_service,
    get_user_problem_rating_repository,
    get_session_repository,
)


router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


class RatingRequest(BaseModel):
    difficulty_rating: Optional[int] = None
    usefulness_rating: Optional[int] = None
    interest_rating: Optional[int] = None
    quality_rating: Optional[int] = None


class PreferenceRequest(BaseModel):
    recommender_type: str


def get_current_user_id(
    request: Request,
    session_repository: SessionRepository = Depends(get_session_repository),
) -> int:
    session_token = request.cookies.get("session_token")

    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user_id = session_repository.get_user_id(session_token)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid session")

    return user_id


@router.get("")
async def get_recommendations(
    request: Request,
    recommender_type: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    user_id: int = Depends(get_current_user_id),
):
    try:
        results = await recommendation_service.get_recommendations(
            user_id, recommender_type, limit
        )
        return {"recommendations": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get recommendations: {str(e)}"
        )


@router.get("/types")
async def get_recommendation_types(
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
):
    types = await recommendation_service.get_available_types()
    return {"types": types}


@router.put("/preferences")
async def set_preference(
    request: Request,
    preference: PreferenceRequest,
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    user_id: int = Depends(get_current_user_id),
):
    try:
        await recommendation_service.set_user_preference(
            user_id, preference.recommender_type
        )
        return {
            "message": "Preference updated",
            "recommender_type": preference.recommender_type,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to set preference: {str(e)}"
        )


@router.post("/problems/{contest_id}/{problem_index}/rate")
async def rate_problem(
    request: Request,
    contest_id: int,
    problem_index: str,
    rating: RatingRequest,
    rating_repository: UserProblemRatingRepository = Depends(
        get_user_problem_rating_repository
    ),
    user_id: int = Depends(get_current_user_id),
):
    try:
        existing = await rating_repository.find_by_user_and_problem(
            user_id, contest_id, problem_index
        )

        if existing:
            existing.difficulty_rating = rating.difficulty_rating
            existing.usefulness_rating = rating.usefulness_rating
            existing.interest_rating = rating.interest_rating
            existing.quality_rating = rating.quality_rating
            await rating_repository.update(existing)
        else:
            new_rating = UserProblemRating(
                user_id=user_id,
                contest_id=contest_id,
                problem_index=problem_index,
                difficulty_rating=rating.difficulty_rating,
                usefulness_rating=rating.usefulness_rating,
                interest_rating=rating.interest_rating,
                quality_rating=rating.quality_rating,
            )
            await rating_repository.create(new_rating)

        return {"message": "Rating saved"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save rating: {str(e)}")


@router.get("/problems/{contest_id}/{problem_index}/ratings")
async def get_problem_ratings(
    contest_id: int,
    problem_index: str,
    rating_repository: UserProblemRatingRepository = Depends(
        get_user_problem_rating_repository
    ),
):
    try:
        ratings = await rating_repository.find_by_problem(contest_id, problem_index)
        return {"ratings": ratings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get ratings: {str(e)}")
