from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from typing import Optional

from domain.models.user import User
from domain.repositories.contests import ContestRepository
from domain.repositories.user_contest_participation import (
    UserContestParticipationRepository,
)
from web.dependencies import get_current_user
from web.utils import get_template_engine
from rest.dependencies import (
    get_contest_repository,
    get_participation_repository,
)

router = APIRouter()
templates = get_template_engine()


@router.get("/contests", response_class=HTMLResponse)
async def contests_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    phase: Optional[str] = Query(None),
    contest_type: Optional[str] = Query(None),
    contest_repository: ContestRepository = Depends(get_contest_repository),
    participation_repository: UserContestParticipationRepository = Depends(
        get_participation_repository
    ),
):
    contests = await contest_repository.find_all()

    filtered_contests = []

    for contest in contests:
        if phase and contest.phase != phase:
            continue
        if contest_type and contest.contest_type != contest_type:
            continue
        filtered_contests.append(contest)

    participations = set()
    if current_user and current_user.id:
        user_participations = await participation_repository.find_by_user_id(
            current_user.id
        )
        participations = {p.contest_id for p in user_participations if p.participated}

    return templates.TemplateResponse(
        "pages/contests.html",
        {
            "request": request,
            "current_user": current_user,
            "contests": sorted(
                filtered_contests, key=lambda x: x.start_time_seconds or 0, reverse=True
            )[:100],
            "participations": participations,
            "phase": phase,
            "contest_type": contest_type,
        },
    )
