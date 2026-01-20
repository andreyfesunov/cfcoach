from contextlib import asynccontextmanager
from fastapi import FastAPI
from rest.routers.auth import router as auth_router
from rest.dependencies import (
    get_event_bus,
    get_codeforces_repository,
    get_user_repository,
    get_submission_repository,
    get_problem_repository,
    get_contest_repository,
    get_rating_change_repository,
    get_participation_repository,
    get_problem_status_repository,
    get_recommendation_service,
    get_recommendation_cache_repository,
    get_config,
)
from application.handlers.user_data_ingestion import UserDataIngestionHandler
from application.jobs.sync_user_data import SyncUserDataJob
from application.jobs.collect_global_data import CollectGlobalDataJob
from application.jobs.update_user_participation import UpdateUserParticipationJob
from application.jobs.update_problem_status import UpdateProblemStatusJob
from application.jobs.train_recommendation_models import TrainRecommendationModelsJob
from application.jobs.update_recommendation_cache import UpdateRecommendationCacheJob
from application.jobs.scheduler import MultiScheduler
from domain.events.user_authenticated import UserAuthenticatedEvent
from rest.routers.recommendations import router as recommendations_router
import uvicorn


def setup_event_handlers():
    event_bus = get_event_bus()
    handler = UserDataIngestionHandler(
        codeforces_repository=get_codeforces_repository(),
        submission_repository=get_submission_repository(),
        problem_repository=get_problem_repository(),
        contest_repository=get_contest_repository(),
        rating_change_repository=get_rating_change_repository(),
    )

    async def handle_event(event: UserAuthenticatedEvent):
        await handler.handle(event)

    event_bus.subscribe(UserAuthenticatedEvent, handle_event)


async def setup_jobs():
    config = get_config()
    scheduler = MultiScheduler()

    sync_job = SyncUserDataJob(
        user_repository=get_user_repository(),
        codeforces_repository=get_codeforces_repository(),
        submission_repository=get_submission_repository(),
        rating_change_repository=get_rating_change_repository(),
    )
    scheduler.add_job(sync_job.execute, config.jobs.sync_interval_hours)

    participation_job = UpdateUserParticipationJob(
        user_repository=get_user_repository(),
        submission_repository=get_submission_repository(),
        rating_change_repository=get_rating_change_repository(),
        participation_repository=get_participation_repository(),
    )
    scheduler.add_job(participation_job.execute, config.jobs.sync_interval_hours)

    problem_status_job = UpdateProblemStatusJob(
        user_repository=get_user_repository(),
        submission_repository=get_submission_repository(),
        problem_status_repository=get_problem_status_repository(),
    )
    scheduler.add_job(problem_status_job.execute, config.jobs.sync_interval_hours)

    global_data_job = CollectGlobalDataJob(
        codeforces_repository=get_codeforces_repository(),
        contest_repository=get_contest_repository(),
        problem_repository=get_problem_repository(),
        submission_repository=get_submission_repository(),
        user_repository=get_user_repository(),
    )
    scheduler.add_job(
        global_data_job.execute, config.jobs.global_data_collection_interval_hours
    )

    training_job = TrainRecommendationModelsJob(
        recommendation_service=get_recommendation_service(),
    )
    scheduler.add_job(
        training_job.execute, config.recommendations.model_training_interval_hours
    )

    cache_job = UpdateRecommendationCacheJob(
        recommendation_service=get_recommendation_service(),
        cache_repository=get_recommendation_cache_repository(),
        user_repository=get_user_repository(),
    )
    scheduler.add_job(
        cache_job.execute, config.recommendations.cache_update_interval_hours
    )

    await scheduler.start_all()
    return scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_event_handlers()
    scheduler = await setup_jobs()
    yield
    await scheduler.stop_all()


app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(recommendations_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
