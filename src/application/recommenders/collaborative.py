from collections import defaultdict
from domain.repositories.user_problem_status import UserProblemStatusRepository
from domain.repositories.users import UserRepository
from domain.repositories.problems import ProblemRepository
from application.recommenders.base import Recommender, RecommendationResult


class CollaborativeFilteringRecommender(Recommender):
    def __init__(
        self,
        user_problem_status_repository: UserProblemStatusRepository,
        user_repository: UserRepository,
        problem_repository: ProblemRepository,
    ):
        self.user_problem_status_repository = user_problem_status_repository
        self.user_repository = user_repository
        self.problem_repository = problem_repository
        self._trained = False
        self._user_similarity: dict[tuple[int, int], float] = {}

    def get_type(self) -> str:
        return "collaborative"

    async def needs_training(self) -> bool:
        return not self._trained

    async def train(self) -> None:
        users = await self.user_repository.find_all()

        user_problems: dict[int, set[tuple[int | None, str | None]]] = {}

        for user in users:
            if user.id is None:
                continue

            solved = await self.user_problem_status_repository.find_solved_by_user_id(
                user.id
            )

            problem_set: set[tuple[int | None, str | None]] = set()
            for status in solved:
                problem_set.add((status.contest_id, status.problem_index))

            if problem_set:
                user_problems[user.id] = problem_set

        self._user_similarity = {}

        user_list = list(user_problems.keys())

        for i in range(len(user_list)):
            for j in range(i + 1, len(user_list)):
                user1_id = user_list[i]
                user2_id = user_list[j]

                problems1 = user_problems[user1_id]
                problems2 = user_problems[user2_id]

                intersection = problems1 & problems2
                union = problems1 | problems2

                if len(union) == 0:
                    similarity = 0.0
                else:
                    similarity = len(intersection) / len(union)

                self._user_similarity[(user1_id, user2_id)] = similarity
                self._user_similarity[(user2_id, user1_id)] = similarity

        self._trained = True

    def _get_similarity(self, user1_id: int, user2_id: int) -> float:
        if user1_id == user2_id:
            return 1.0
        return self._user_similarity.get((user1_id, user2_id), 0.0)

    async def recommend(
        self, user_id: int, limit: int = 10
    ) -> list[RecommendationResult]:
        if not self._trained:
            await self.train()

        solved_statuses = (
            await self.user_problem_status_repository.find_solved_by_user_id(user_id)
        )
        solved_problems: set[tuple[int | None, str | None]] = {
            (s.contest_id, s.problem_index) for s in solved_statuses
        }

        users = await self.user_repository.find_all()

        problem_scores: dict[tuple[int | None, str | None], float] = defaultdict(float)

        for other_user in users:
            if other_user.id is None or other_user.id == user_id:
                continue

            similarity = self._get_similarity(user_id, other_user.id)

            if similarity <= 0:
                continue

            other_solved = (
                await self.user_problem_status_repository.find_solved_by_user_id(
                    other_user.id
                )
            )

            for status in other_solved:
                problem_key = (status.contest_id, status.problem_index)

                if problem_key not in solved_problems:
                    problem_scores[problem_key] += similarity

        recommendations: list[tuple[RecommendationResult, float]] = []

        for (contest_id, problem_index), score in problem_scores.items():
            if not contest_id or not problem_index:
                continue

            problem = await self.problem_repository.find_by_contest_and_index(
                contest_id, problem_index
            )

            if problem and score > 0:
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
