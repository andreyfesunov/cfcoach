from domain.repositories.users import UserRepository
from domain.repositories.codeforces import CodeforcesRepository
from domain.repositories.submissions import SubmissionRepository
from domain.repositories.rating_changes import RatingChangeRepository
from domain.models.submission import Submission
from domain.models.rating_change import RatingChange


class SyncUserDataJob:
    def __init__(
        self,
        user_repository: UserRepository,
        codeforces_repository: CodeforcesRepository,
        submission_repository: SubmissionRepository,
        rating_change_repository: RatingChangeRepository,
    ):
        self.user_repository = user_repository
        self.codeforces_repository = codeforces_repository
        self.submission_repository = submission_repository
        self.rating_change_repository = rating_change_repository

    async def execute(self) -> None:
        users = await self.user_repository.find_all()

        for user in users:
            if not user.access_token or not user.username or user.id is None:
                continue

            try:
                submissions_data = self.codeforces_repository.get_user_submissions(
                    user.username, user.access_token, from_index=1, count=1000
                )

                submissions = []
                for sub_data in submissions_data:
                    existing = await self.submission_repository.find_by_submission_id(
                        sub_data["id"]
                    )
                    if not existing:
                        submission = Submission(
                            user_id=user.id,
                            submission_id=sub_data["id"],
                            contest_id=sub_data.get("contestId"),
                            problem_index=sub_data.get("problem", {}).get("index"),
                            problem_name=sub_data.get("problem", {}).get("name"),
                            verdict=sub_data.get("verdict", "UNKNOWN"),
                            programming_language=sub_data.get(
                                "programmingLanguage", ""
                            ),
                            creation_time_seconds=sub_data.get(
                                "creationTimeSeconds", 0
                            ),
                        )
                        submissions.append(submission)

                if submissions:
                    await self.submission_repository.create_many(submissions)

                rating_data = self.codeforces_repository.get_user_rating(
                    user.username, user.access_token
                )

                latest_rating = (
                    await self.rating_change_repository.find_latest_by_user_id(
                        user.id, limit=1
                    )
                )
                latest_rating_time = (
                    latest_rating[0].rating_update_time_seconds if latest_rating else 0
                )

                rating_changes = []
                for rating_item in rating_data:
                    if (
                        rating_item.get("ratingUpdateTimeSeconds", 0)
                        > latest_rating_time
                    ):
                        existing = await self.rating_change_repository.find_by_user_and_contest(
                            user.id, rating_item.get("contestId", 0)
                        )
                        if not existing:
                            rating_change = RatingChange(
                                user_id=user.id,
                                contest_id=rating_item.get("contestId", 0),
                                contest_name=rating_item.get("contestName", ""),
                                handle=user.username,
                                rank=rating_item.get("rank", 0),
                                rating_update_time_seconds=rating_item.get(
                                    "ratingUpdateTimeSeconds", 0
                                ),
                                old_rating=rating_item.get("oldRating", 0),
                                new_rating=rating_item.get("newRating", 0),
                            )
                            rating_changes.append(rating_change)

                if rating_changes:
                    await self.rating_change_repository.create_many(rating_changes)

            except Exception as e:
                import logging

                logging.error(
                    f"Failed to sync data for user {user.id} (handle: {user.username}): {e}"
                )
