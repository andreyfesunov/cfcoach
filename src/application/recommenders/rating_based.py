from collections import defaultdict
from domain.repositories.user_problem_rating import UserProblemRatingRepository
from domain.repositories.user_problem_status import UserProblemStatusRepository
from domain.repositories.problems import ProblemRepository
from domain.repositories.users import UserRepository
from application.recommenders.base import Recommender, RecommendationResult


class RatingBasedRecommender(Recommender):
    def __init__(
        self,
        user_problem_rating_repository: UserProblemRatingRepository,
        user_problem_status_repository: UserProblemStatusRepository,
        problem_repository: ProblemRepository,
        user_repository: UserRepository,
    ):
        self.user_problem_rating_repository = user_problem_rating_repository
        self.user_problem_status_repository = user_problem_status_repository
        self.problem_repository = problem_repository
        self.user_repository = user_repository
        self._trained = False

    def get_type(self) -> str:
        return "rating_based"

    async def needs_training(self) -> bool:
        return not self._trained

    async def train(self) -> None:
        self._trained = True

    async def recommend(
        self, user_id: int, limit: int = 10
    ) -> list[RecommendationResult]:
        user_ratings = await self.user_problem_rating_repository.find_by_user_id(
            user_id
        )

        if not user_ratings:
            return []

        solved_statuses = (
            await self.user_problem_status_repository.find_solved_by_user_id(user_id)
        )
        solved_problems: set[tuple[int | None, str | None]] = {
            (s.contest_id, s.problem_index) for s in solved_statuses
        }

        problem_scores: dict[
            tuple[int | None, str | None], dict[str, list[int]]
        ] = defaultdict(lambda: defaultdict(list))

        for rating in user_ratings:
            if not rating.contest_id or not rating.problem_index:
                continue

            problem_key = (rating.contest_id, rating.problem_index)

            if rating.difficulty_rating:
                problem_scores[problem_key]["difficulty"].append(
                    rating.difficulty_rating
                )
            if rating.usefulness_rating:
                problem_scores[problem_key]["usefulness"].append(
                    rating.usefulness_rating
                )
            if rating.interest_rating:
                problem_scores[problem_key]["interest"].append(rating.interest_rating)
            if rating.quality_rating:
                problem_scores[problem_key]["quality"].append(rating.quality_rating)

        all_ratings = await self.user_problem_rating_repository.find_by_user_id(user_id)

        for rating in all_ratings:
            if not rating.contest_id or not rating.problem_index:
                continue

            problem_key = (rating.contest_id, rating.problem_index)

            if problem_key in solved_problems:
                continue

            if problem_key not in problem_scores:
                problem_scores[problem_key] = defaultdict(list)

            if rating.difficulty_rating:
                problem_scores[problem_key]["difficulty"].append(
                    rating.difficulty_rating
                )
            if rating.usefulness_rating:
                problem_scores[problem_key]["usefulness"].append(
                    rating.usefulness_rating
                )
            if rating.interest_rating:
                problem_scores[problem_key]["interest"].append(rating.interest_rating)
            if rating.quality_rating:
                problem_scores[problem_key]["quality"].append(rating.quality_rating)

        users = await self.user_repository.find_all()

        for other_user in users:
            if other_user.id is None or other_user.id == user_id:
                continue

            other_ratings = await self.user_problem_rating_repository.find_by_user_id(
                other_user.id
            )

            for rating in other_ratings:
                if not rating.contest_id or not rating.problem_index:
                    continue

                problem_key = (rating.contest_id, rating.problem_index)

                if problem_key in solved_problems:
                    continue

                if rating.difficulty_rating:
                    problem_scores[problem_key]["difficulty"].append(
                        rating.difficulty_rating
                    )
                if rating.usefulness_rating:
                    problem_scores[problem_key]["usefulness"].append(
                        rating.usefulness_rating
                    )
                if rating.interest_rating:
                    problem_scores[problem_key]["interest"].append(
                        rating.interest_rating
                    )
                if rating.quality_rating:
                    problem_scores[problem_key]["quality"].append(rating.quality_rating)

        recommendations: list[tuple[RecommendationResult, float]] = []

        for (contest_id, problem_index), scores in problem_scores.items():
            if not contest_id or not problem_index:
                continue

            if (contest_id, problem_index) in solved_problems:
                continue

            problem = await self.problem_repository.find_by_contest_and_index(
                contest_id, problem_index
            )

            if not problem:
                continue

            total_score = 0.0
            weight_sum = 0.0

            if scores["usefulness"]:
                avg_usefulness = sum(scores["usefulness"]) / len(scores["usefulness"])
                total_score += avg_usefulness * 0.4
                weight_sum += 0.4

            if scores["interest"]:
                avg_interest = sum(scores["interest"]) / len(scores["interest"])
                total_score += avg_interest * 0.3
                weight_sum += 0.3

            if scores["quality"]:
                avg_quality = sum(scores["quality"]) / len(scores["quality"])
                total_score += avg_quality * 0.3
                weight_sum += 0.3

            if weight_sum > 0:
                final_score = total_score / weight_sum

                if final_score > 0:
                    recommendations.append(
                        (
                            RecommendationResult(
                                problem_id=problem.id or 0,
                                contest_id=problem.contest_id,
                                problem_index=problem.problem_index,
                                score=final_score,
                            ),
                            final_score,
                        )
                    )

        recommendations.sort(key=lambda x: x[1], reverse=True)

        return [rec[0] for rec in recommendations[:limit]]
