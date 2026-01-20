from domain.repositories.codeforces import CodeforcesRepository
from domain.repositories.contests import ContestRepository
from domain.repositories.problems import ProblemRepository
from domain.repositories.submissions import SubmissionRepository
from domain.repositories.users import UserRepository
from domain.models.contest import Contest
from domain.models.problem import Problem
from domain.models.submission import Submission
import asyncio


class CollectGlobalDataJob:
    def __init__(
        self,
        codeforces_repository: CodeforcesRepository,
        contest_repository: ContestRepository,
        problem_repository: ProblemRepository,
        submission_repository: SubmissionRepository,
        user_repository: UserRepository,
    ):
        self.codeforces_repository = codeforces_repository
        self.contest_repository = contest_repository
        self.problem_repository = problem_repository
        self.submission_repository = submission_repository
        self.user_repository = user_repository

    async def execute(self) -> None:
        try:
            contests_data = self.codeforces_repository.get_contest_list(gym=False)
            contests = []
            for contest_data in contests_data:
                contest = Contest(
                    contest_id=contest_data.get("id", 0),
                    name=contest_data.get("name", ""),
                    contest_type=contest_data.get("type"),
                    phase=contest_data.get("phase"),
                    frozen=contest_data.get("frozen"),
                    duration_seconds=contest_data.get("durationSeconds"),
                    start_time_seconds=contest_data.get("startTimeSeconds"),
                    relative_time_seconds=contest_data.get("relativeTimeSeconds"),
                    prepared_by=contest_data.get("preparedBy"),
                    website_url=contest_data.get("websiteUrl"),
                    description=contest_data.get("description"),
                    difficulty=contest_data.get("difficulty"),
                    kind=contest_data.get("kind"),
                    icpc_region=contest_data.get("icpcRegion"),
                    country=contest_data.get("country"),
                    city=contest_data.get("city"),
                    season=contest_data.get("season"),
                )
                contests.append(contest)
            if contests:
                await self.contest_repository.create_many(contests)

            problems_data = self.codeforces_repository.get_problem_set()
            problems = []
            for problem_data in problems_data:
                problem = Problem(
                    contest_id=problem_data.get("contestId"),
                    problem_index=problem_data.get("index"),
                    name=problem_data.get("name", ""),
                    problem_type=problem_data.get("type"),
                    points=problem_data.get("points"),
                    rating=problem_data.get("rating"),
                    tags=problem_data.get("tags", []),
                )
                problems.append(problem)
            if problems:
                await self.problem_repository.create_many(problems)

            rated_users = self.codeforces_repository.get_rated_users(active_only=True)
            top_users = rated_users[:100]

            for user_data in top_users:
                handle = user_data.get("handle")
                if not handle:
                    continue

                try:
                    await asyncio.sleep(1)

                    submissions_data = self.codeforces_repository.get_user_submissions(
                        handle, from_index=1, count=100
                    )

                    user = await self.user_repository.find_by_username(handle)
                    if not user:
                        from domain.models.user import User

                        user = User(
                            external_id=None,
                            username=handle,
                            access_token=None,
                        )
                        user = await self.user_repository.create(user)

                    if user.id is None:
                        continue

                    submissions = []
                    for sub_data in submissions_data:
                        existing = (
                            await self.submission_repository.find_by_submission_id(
                                sub_data["id"]
                            )
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

                except Exception:
                    pass

        except Exception as e:
            import logging

            logging.error(f"Failed to collect global data: {e}")
