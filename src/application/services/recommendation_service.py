from typing import Optional
from datetime import datetime, timedelta
from domain.repositories.user_preferences import UserPreferencesRepository
from domain.repositories.recommendation_cache import RecommendationCacheRepository
from domain.models.recommendation_cache import RecommendationCache
from application.recommenders.base import Recommender, RecommendationResult


class RecommendationService:
    def __init__(
        self,
        recommenders: dict[str, Recommender],
        user_preferences_repository: UserPreferencesRepository,
        cache_repository: RecommendationCacheRepository,
        cache_ttl_hours: float = 1.0,
    ):
        self.recommenders = recommenders
        self.user_preferences_repository = user_preferences_repository
        self.cache_repository = cache_repository
        self.cache_ttl_hours = cache_ttl_hours

    async def get_recommendations(
        self, user_id: int, recommender_type: Optional[str] = None, limit: int = 10
    ) -> list[RecommendationResult]:
        if recommender_type is None:
            preferences = await self.user_preferences_repository.find_by_user_id(
                user_id
            )
            if preferences:
                recommender_type = preferences.preferred_recommender_type
            else:
                recommender_type = "content_based"

        if recommender_type not in self.recommenders:
            recommender_type = "content_based"

        cached = await self.cache_repository.find_by_user_and_type(
            user_id, recommender_type
        )

        if cached:
            results: list[RecommendationResult] = []
            for i, problem_id in enumerate(cached.problem_ids):
                if i < len(cached.scores):
                    results.append(
                        RecommendationResult(
                            problem_id=problem_id,
                            contest_id=None,
                            problem_index=None,
                            score=cached.scores[i],
                        )
                    )
            return results

        recommender = self.recommenders[recommender_type]

        if await recommender.needs_training():
            await recommender.train()

        results = await recommender.recommend(user_id, limit)

        if results:
            problem_ids = [r["problem_id"] for r in results]
            scores = [r["score"] for r in results]

            expires_at = datetime.now() + timedelta(hours=self.cache_ttl_hours)

            cache = RecommendationCache(
                user_id=user_id,
                recommender_type=recommender_type,
                problem_ids=problem_ids,
                scores=scores,
                expires_at=expires_at,
            )

            await self.cache_repository.create(cache)

        return results

    async def get_available_types(self) -> list[str]:
        return list(self.recommenders.keys())

    async def set_user_preference(self, user_id: int, recommender_type: str) -> None:
        if recommender_type not in self.recommenders:
            raise ValueError(f"Unknown recommender type: {recommender_type}")

        from domain.models.user_preferences import UserPreferences

        preferences = await self.user_preferences_repository.find_by_user_id(user_id)

        if preferences:
            preferences.preferred_recommender_type = recommender_type
            await self.user_preferences_repository.update(preferences)
        else:
            preferences = UserPreferences(
                user_id=user_id, preferred_recommender_type=recommender_type
            )
            await self.user_preferences_repository.create(preferences)

        await self.cache_repository.delete_by_user_and_type(user_id, recommender_type)
