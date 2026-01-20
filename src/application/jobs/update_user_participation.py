from domain.repositories.users import UserRepository
from domain.repositories.submissions import SubmissionRepository
from domain.repositories.rating_changes import RatingChangeRepository
from domain.repositories.user_contest_participation import (
    UserContestParticipationRepository,
)
from domain.models.user_contest_participation import UserContestParticipation


class UpdateUserParticipationJob:
    def __init__(
        self,
        user_repository: UserRepository,
        submission_repository: SubmissionRepository,
        rating_change_repository: RatingChangeRepository,
        participation_repository: UserContestParticipationRepository,
    ):
        self.user_repository = user_repository
        self.submission_repository = submission_repository
        self.rating_change_repository = rating_change_repository
        self.participation_repository = participation_repository

    async def execute(self) -> None:
        users = await self.user_repository.find_all()

        for user in users:
            if user.id is None:
                continue

            try:
                rating_changes = await self.rating_change_repository.find_by_user_id(
                    user.id
                )

                contest_participation = {}

                for rating_change in rating_changes:
                    contest_id = rating_change.contest_id
                    if contest_id not in contest_participation:
                        contest_participation[contest_id] = {
                            "participated": True,
                            "first_submission_time": rating_change.rating_update_time_seconds,
                            "last_submission_time": rating_change.rating_update_time_seconds,
                        }

                submissions = await self.submission_repository.find_by_user_id(user.id)

                for submission in submissions:
                    if submission.contest_id:
                        contest_id = submission.contest_id
                        if contest_id not in contest_participation:
                            contest_participation[contest_id] = {
                                "participated": True,
                                "first_submission_time": submission.creation_time_seconds,
                                "last_submission_time": submission.creation_time_seconds,
                            }
                        else:
                            part = contest_participation[contest_id]
                            if (
                                part["first_submission_time"] is None
                                or submission.creation_time_seconds
                                < part["first_submission_time"]
                            ):
                                part[
                                    "first_submission_time"
                                ] = submission.creation_time_seconds
                            if (
                                part["last_submission_time"] is None
                                or submission.creation_time_seconds
                                > part["last_submission_time"]
                            ):
                                part[
                                    "last_submission_time"
                                ] = submission.creation_time_seconds

                for contest_id, part_data in contest_participation.items():
                    existing = (
                        await self.participation_repository.find_by_user_and_contest(
                            user.id, contest_id
                        )
                    )

                    participation = UserContestParticipation(
                        id=existing.id if existing else None,
                        user_id=user.id,
                        contest_id=contest_id,
                        participated=part_data["participated"],
                        first_submission_time=part_data.get("first_submission_time"),
                        last_submission_time=part_data.get("last_submission_time"),
                    )

                    if existing:
                        await self.participation_repository.update(participation)
                    else:
                        await self.participation_repository.create(participation)

            except Exception as e:
                import logging

                logging.error(f"Failed to update participation for user {user.id}: {e}")
