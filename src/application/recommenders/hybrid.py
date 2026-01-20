from application.recommenders.base import Recommender, RecommendationResult
from application.recommenders.content_based import ContentBasedRecommender
from application.recommenders.collaborative import CollaborativeFilteringRecommender


class HybridRecommender(Recommender):
    def __init__(
        self,
        content_based: ContentBasedRecommender,
        collaborative: CollaborativeFilteringRecommender,
        content_weight: float = 0.6,
        collaborative_weight: float = 0.4,
    ):
        self.content_based = content_based
        self.collaborative = collaborative
        self.content_weight = content_weight
        self.collaborative_weight = collaborative_weight

    def get_type(self) -> str:
        return "hybrid"

    async def needs_training(self) -> bool:
        return (
            await self.content_based.needs_training()
            or await self.collaborative.needs_training()
        )

    async def train(self) -> None:
        if await self.content_based.needs_training():
            await self.content_based.train()
        if await self.collaborative.needs_training():
            await self.collaborative.train()

    async def recommend(
        self, user_id: int, limit: int = 10
    ) -> list[RecommendationResult]:
        content_results = await self.content_based.recommend(user_id, limit * 2)
        collaborative_results = await self.collaborative.recommend(user_id, limit * 2)

        problem_scores: dict[tuple[int | None, str | None], tuple[float, float]] = {}

        for result in content_results:
            key = (result["contest_id"], result["problem_index"])
            current = problem_scores.get(key, (0.0, 0.0))
            problem_scores[key] = (
                current[0] + result["score"] * self.content_weight,
                current[1],
            )

        for result in collaborative_results:
            key = (result["contest_id"], result["problem_index"])
            current = problem_scores.get(key, (0.0, 0.0))
            problem_scores[key] = (
                current[0],
                current[1] + result["score"] * self.collaborative_weight,
            )

        recommendations: list[tuple[RecommendationResult, float]] = []

        problem_repo = None
        if hasattr(self.content_based, "problem_repository"):
            problem_repo = self.content_based.problem_repository

        for (contest_id, problem_index), (
            content_score,
            collab_score,
        ) in problem_scores.items():
            if not contest_id or not problem_index:
                continue

            total_score = content_score + collab_score

            if total_score > 0:
                problem_id = 0
                if problem_repo:
                    problem = await problem_repo.find_by_contest_and_index(
                        contest_id, problem_index
                    )
                    if problem and problem.id:
                        problem_id = problem.id

                recommendations.append(
                    (
                        RecommendationResult(
                            problem_id=problem_id,
                            contest_id=contest_id,
                            problem_index=problem_index,
                            score=total_score,
                        ),
                        total_score,
                    )
                )

        recommendations.sort(key=lambda x: x[1], reverse=True)

        return [rec[0] for rec in recommendations[:limit]]
