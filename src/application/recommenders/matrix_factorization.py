from domain.repositories.user_problem_status import UserProblemStatusRepository
from domain.repositories.users import UserRepository
from domain.repositories.problems import ProblemRepository
from application.recommenders.base import Recommender, RecommendationResult


class MatrixFactorizationRecommender(Recommender):
    def __init__(
        self,
        user_problem_status_repository: UserProblemStatusRepository,
        user_repository: UserRepository,
        problem_repository: ProblemRepository,
        n_factors: int = 10,
        learning_rate: float = 0.01,
        regularization: float = 0.1,
        n_iterations: int = 20,
    ):
        self.user_problem_status_repository = user_problem_status_repository
        self.user_repository = user_repository
        self.problem_repository = problem_repository
        self.n_factors = n_factors
        self.learning_rate = learning_rate
        self.regularization = regularization
        self.n_iterations = n_iterations
        self._trained = False
        self._user_factors: dict[int, list[float]] = {}
        self._problem_factors: dict[tuple[int | None, str | None], list[float]] = {}
        self._user_index: dict[int, int] = {}
        self._problem_index: dict[tuple[int | None, str | None], int] = {}

    def get_type(self) -> str:
        return "matrix_factorization"

    async def needs_training(self) -> bool:
        return not self._trained

    async def train(self) -> None:
        users = await self.user_repository.find_all()
        user_problems: dict[int, set[tuple[int | None, str | None]]] = {}

        all_problems: set[tuple[int | None, str | None]] = set()

        for user in users:
            if user.id is None:
                continue

            solved = await self.user_problem_status_repository.find_solved_by_user_id(
                user.id
            )

            problem_set: set[tuple[int | None, str | None]] = set()
            for status in solved:
                problem_key = (status.contest_id, status.problem_index)
                problem_set.add(problem_key)
                all_problems.add(problem_key)

            if problem_set:
                user_problems[user.id] = problem_set

        user_list = list(user_problems.keys())
        problem_list = list(all_problems)

        for idx, user_id in enumerate(user_list):
            self._user_index[user_id] = idx
            self._user_factors[user_id] = [
                0.1 * (i % 5 - 2) for i in range(self.n_factors)
            ]

        for idx, problem_key in enumerate(problem_list):
            self._problem_index[problem_key] = idx
            self._problem_factors[problem_key] = [
                0.1 * (i % 5 - 2) for i in range(self.n_factors)
            ]

        for iteration in range(self.n_iterations):
            for user_id, problems in user_problems.items():
                user_factors = self._user_factors[user_id]

                for problem_key in problems:
                    if problem_key not in self._problem_factors:
                        continue

                    problem_factors = self._problem_factors[problem_key]

                    prediction = sum(
                        user_factors[i] * problem_factors[i]
                        for i in range(self.n_factors)
                    )

                    error = 1.0 - prediction

                    for i in range(self.n_factors):
                        user_factor = user_factors[i]
                        problem_factor = problem_factors[i]

                        user_factors[i] += self.learning_rate * (
                            error * problem_factor - self.regularization * user_factor
                        )
                        problem_factors[i] += self.learning_rate * (
                            error * user_factor - self.regularization * problem_factor
                        )

        self._trained = True

    async def recommend(
        self, user_id: int, limit: int = 10
    ) -> list[RecommendationResult]:
        if not self._trained:
            await self.train()

        if user_id not in self._user_factors:
            return []

        user_factors = self._user_factors[user_id]

        solved_statuses = (
            await self.user_problem_status_repository.find_solved_by_user_id(user_id)
        )
        solved_problems: set[tuple[int | None, str | None]] = {
            (s.contest_id, s.problem_index) for s in solved_statuses
        }

        recommendations: list[tuple[RecommendationResult, float]] = []

        for problem_key, problem_factors in self._problem_factors.items():
            if problem_key in solved_problems:
                continue

            if not problem_key[0] or not problem_key[1]:
                continue

            prediction = sum(
                user_factors[i] * problem_factors[i] for i in range(self.n_factors)
            )

            if prediction > 0:
                problem = await self.problem_repository.find_by_contest_and_index(
                    problem_key[0], problem_key[1]
                )

                if problem:
                    recommendations.append(
                        (
                            RecommendationResult(
                                problem_id=problem.id or 0,
                                contest_id=problem.contest_id,
                                problem_index=problem.problem_index,
                                score=prediction,
                            ),
                            prediction,
                        )
                    )

        recommendations.sort(key=lambda x: x[1], reverse=True)

        return [rec[0] for rec in recommendations[:limit]]
