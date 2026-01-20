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
    get_config,
)
from application.handlers.user_data_ingestion import UserDataIngestionHandler
from application.jobs.sync_user_data import SyncUserDataJob
from application.jobs.scheduler import Scheduler
from domain.events.user_authenticated import UserAuthenticatedEvent
import uvicorn


app = FastAPI()

app.include_router(auth_router)


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
    scheduler = Scheduler(interval_hours=config.jobs.sync_interval_hours)
    job = SyncUserDataJob(
        user_repository=get_user_repository(),
        codeforces_repository=get_codeforces_repository(),
        submission_repository=get_submission_repository(),
        rating_change_repository=get_rating_change_repository(),
    )
    await scheduler.start(job.execute)


@app.on_event("startup")
async def startup():
    setup_event_handlers()
    await setup_jobs()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
