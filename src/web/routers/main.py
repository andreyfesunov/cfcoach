from fastapi import APIRouter

from web.routers import (
    dashboard,
    profile,
    recommendations,
    settings,
    rate,
    problems,
    contests,
    progress,
    comparison,
)

router = APIRouter()

router.include_router(dashboard.router)
router.include_router(profile.router)
router.include_router(recommendations.router)
router.include_router(settings.router)
router.include_router(rate.router)
router.include_router(problems.router)
router.include_router(contests.router)
router.include_router(progress.router)
router.include_router(comparison.router)
