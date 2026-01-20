from domain.repositories.user_problem_status import UserProblemStatusRepository
from domain.repositories.problems import ProblemRepository
from domain.repositories.users import UserRepository
from domain.repositories.submissions import SubmissionRepository
from application.recommenders.base import Recommender, RecommendationResult


class ContentBasedRecommender(Recommender):
    def __init__(
        self,
        user_problem_status_repository: UserProblemStatusRepository,
        problem_repository: ProblemRepository,
        user_repository: UserRepository,
        submission_repository: SubmissionRepository,
    ):
        self.user_problem_status_repository = user_problem_status_repository
        self.problem_repository = problem_repository
        self.user_repository = user_repository
        self.submission_repository = submission_repository
        self._trained = False

    def get_type(self) -> str:
        return "content_based"

    async def needs_training(self) -> bool:
        return not self._trained

    async def train(self) -> None:
        self._trained = True

    async def recommend(
        self, user_id: int, limit: int = 10
    ) -> list[RecommendationResult]:
        solved_statuses = (
            await self.user_problem_status_repository.find_solved_by_user_id(user_id)
        )

        if not solved_statuses:
            return []

        tag_weights: dict[str, float] = {}
        rating_sum = 0
        rating_count = 0

        for status in solved_statuses:
            if not status.contest_id or not status.problem_index:
                continue

            problem = await self.problem_repository.find_by_contest_and_index(
                status.contest_id, status.problem_index
            )

            if problem and problem.tags:
                for tag in problem.tags:
                    tag_weights[tag] = tag_weights.get(tag, 0.0) + 1.0

            if problem and problem.rating:
                rating_sum += problem.rating
                rating_count += 1

        if not tag_weights:
            return []

        total_tag_count = sum(tag_weights.values())
        for tag in tag_weights:
            tag_weights[tag] /= total_tag_count

        target_rating = int(rating_sum / rating_count) if rating_count > 0 else None

        unsolved_statuses = (
            await self.user_problem_status_repository.find_unsolved_by_user_id(user_id)
        )

        recommendations: list[tuple[RecommendationResult, float]] = []

        for status in unsolved_statuses:
            if not status.contest_id or not status.problem_index:
                continue

            problem = await self.problem_repository.find_by_contest_and_index(
                status.contest_id, status.problem_index
            )

            if not problem:
                continue

            score = 0.0

            if problem.tags:
                for tag in problem.tags:
                    score += tag_weights.get(tag, 0.0)

            if target_rating and problem.rating:
                rating_diff = abs(problem.rating - target_rating)
                rating_score = 1.0 / (1.0 + rating_diff / 100.0)
                score = score * 0.7 + rating_score * 0.3

            if score > 0:
                recommendations.append(
                    (
                        RecommendationResult(
                            problem_id=problem.id or 0,
                            contest_id=problem.contest_id,
                            problem_index=problem.problem_index,
                            score=score,
                        ),
                        score,
                    )
                )

        recommendations.sort(key=lambda x: x[1], reverse=True)

        return [rec[0] for rec in recommendations[:limit]]
