from domain.repositories.users import UserRepository
from domain.repositories.submissions import SubmissionRepository
from domain.repositories.user_problem_status import UserProblemStatusRepository
from domain.models.user_problem_status import UserProblemStatus


class UpdateProblemStatusJob:
    def __init__(
        self,
        user_repository: UserRepository,
        submission_repository: SubmissionRepository,
        problem_status_repository: UserProblemStatusRepository,
    ):
        self.user_repository = user_repository
        self.submission_repository = submission_repository
        self.problem_status_repository = problem_status_repository

    async def execute(self) -> None:
        users = await self.user_repository.find_all()

        for user in users:
            if user.id is None:
                continue

            try:
                submissions = await self.submission_repository.find_by_user_id(user.id)

                problem_status_map: dict[
                    tuple[int, str], dict[str, bool | int | None]
                ] = {}

                for submission in submissions:
                    if not submission.contest_id or not submission.problem_index:
                        continue

                    key = (submission.contest_id, submission.problem_index)

                    if key not in problem_status_map:
                        problem_status_map[key] = {
                            "solved": False,
                            "attempts_count": 0,
                            "first_solved_time": None,
                            "last_attempt_time": submission.creation_time_seconds,
                        }

                    status = problem_status_map[key]
                    attempts = status.get("attempts_count", 0)
                    if isinstance(attempts, int):
                        status["attempts_count"] = attempts + 1
                    else:
                        status["attempts_count"] = 1

                    if submission.verdict == "OK":
                        status["solved"] = True
                        if (
                            status["first_solved_time"] is None
                            or submission.creation_time_seconds
                            < status["first_solved_time"]
                        ):
                            status[
                                "first_solved_time"
                            ] = submission.creation_time_seconds

                    if (
                        status["last_attempt_time"] is None
                        or submission.creation_time_seconds
                        > status["last_attempt_time"]
                    ):
                        status["last_attempt_time"] = submission.creation_time_seconds

                for (
                    contest_id,
                    problem_index,
                ), status_data in problem_status_map.items():
                    existing = (
                        await self.problem_status_repository.find_by_user_and_problem(
                            user.id, contest_id, problem_index
                        )
                    )

                    problem_status = UserProblemStatus(
                        id=existing.id if existing else None,
                        user_id=user.id,
                        contest_id=contest_id,
                        problem_index=problem_index,
                        solved=status_data["solved"],
                        attempts_count=status_data["attempts_count"],
                        first_solved_time=status_data.get("first_solved_time"),
                        last_attempt_time=status_data.get("last_attempt_time"),
                    )

                    if existing:
                        await self.problem_status_repository.update(problem_status)
                    else:
                        await self.problem_status_repository.create(problem_status)

            except Exception as e:
                import logging

                logging.error(
                    f"Failed to update problem status for user {user.id}: {e}"
                )
