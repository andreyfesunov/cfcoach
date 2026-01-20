from domain.events.user_authenticated import UserAuthenticatedEvent
from domain.repositories.codeforces import CodeforcesRepository
from domain.repositories.submissions import SubmissionRepository
from domain.repositories.problems import ProblemRepository
from domain.repositories.contests import ContestRepository
from domain.repositories.rating_changes import RatingChangeRepository
from domain.models.submission import Submission
from domain.models.problem import Problem
from domain.models.contest import Contest
from domain.models.rating_change import RatingChange


class UserDataIngestionHandler:
    def __init__(
        self,
        codeforces_repository: CodeforcesRepository,
        submission_repository: SubmissionRepository,
        problem_repository: ProblemRepository,
        contest_repository: ContestRepository,
        rating_change_repository: RatingChangeRepository,
    ):
        self.codeforces_repository = codeforces_repository
        self.submission_repository = submission_repository
        self.problem_repository = problem_repository
        self.contest_repository = contest_repository
        self.rating_change_repository = rating_change_repository

    async def handle(self, event: UserAuthenticatedEvent) -> None:
        user_id = event.user_id
        handle = event.username
        access_token = event.access_token

        if not handle:
            return

        try:
            submissions_data = []
            from_index = 1
            count = 1000

            while True:
                batch = self.codeforces_repository.get_user_submissions(
                    handle, access_token, from_index, count
                )
                if not batch:
                    break
                submissions_data.extend(batch)
                if len(batch) < count:
                    break
                from_index += count

            submissions = []
            problems_set: dict[tuple[int | None, str | None], Problem] = {}
            contests_set: dict[int | None, None] = {}

            for sub_data in submissions_data:
                submission = Submission(
                    user_id=user_id,
                    submission_id=sub_data["id"],
                    contest_id=sub_data.get("contestId"),
                    problem_index=sub_data.get("problem", {}).get("index"),
                    problem_name=sub_data.get("problem", {}).get("name"),
                    verdict=sub_data.get("verdict", "UNKNOWN"),
                    programming_language=sub_data.get("programmingLanguage", ""),
                    creation_time_seconds=sub_data.get("creationTimeSeconds", 0),
                )
                submissions.append(submission)

                problem_data = sub_data.get("problem", {})
                if problem_data:
                    problem_key = (
                        problem_data.get("contestId"),
                        problem_data.get("index"),
                    )
                    if problem_key not in problems_set:
                        problem = Problem(
                            contest_id=problem_data.get("contestId"),
                            problem_index=problem_data.get("index"),
                            name=problem_data.get("name", ""),
                            problem_type=problem_data.get("type"),
                            points=problem_data.get("points"),
                            rating=problem_data.get("rating"),
                            tags=problem_data.get("tags", []),
                        )
                        problems_set[problem_key] = problem

                contest_id = sub_data.get("contestId")
                if contest_id and contest_id not in contests_set:
                    contests_set[contest_id] = None

            await self.submission_repository.create_many(submissions)

            if problems_set:
                problems = list(problems_set.values())
                await self.problem_repository.create_many(problems)

            rating_data = self.codeforces_repository.get_user_rating(
                handle, access_token
            )
            rating_changes = []
            contests_from_rating: dict[int | None, None] = {}

            for rating_item in rating_data:
                contest_id = rating_item.get("contestId")
                if contest_id and contest_id not in contests_from_rating:
                    contests_from_rating[contest_id] = None

                rating_change = RatingChange(
                    user_id=user_id,
                    contest_id=contest_id,
                    contest_name=rating_item.get("contestName", ""),
                    handle=handle,
                    rank=rating_item.get("rank", 0),
                    rating_update_time_seconds=rating_item.get(
                        "ratingUpdateTimeSeconds", 0
                    ),
                    old_rating=rating_item.get("oldRating", 0),
                    new_rating=rating_item.get("newRating", 0),
                )
                rating_changes.append(rating_change)

            await self.rating_change_repository.create_many(rating_changes)

            all_contest_ids = set(contests_set.keys()) | set(
                contests_from_rating.keys()
            )
            if all_contest_ids:
                contests_data = self.codeforces_repository.get_contest_list(gym=False)
                contests = []
                for contest_data in contests_data:
                    if contest_data.get("id") in all_contest_ids:
                        contest = Contest(
                            contest_id=contest_data.get("id", 0),
                            name=contest_data.get("name", ""),
                            contest_type=contest_data.get("type"),
                            phase=contest_data.get("phase"),
                            frozen=contest_data.get("frozen"),
                            duration_seconds=contest_data.get("durationSeconds"),
                            start_time_seconds=contest_data.get("startTimeSeconds"),
                            relative_time_seconds=contest_data.get(
                                "relativeTimeSeconds"
                            ),
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
        except Exception as e:
            import logging

            logging.error(
                f"Failed to ingest data for user {user_id} (handle: {handle}): {e}"
            )
