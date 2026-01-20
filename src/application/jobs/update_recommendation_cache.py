from domain.repositories.recommendation_cache import RecommendationCacheRepository
from domain.repositories.users import UserRepository
from application.services.recommendation_service import RecommendationService


class UpdateRecommendationCacheJob:
    def __init__(
        self,
        recommendation_service: RecommendationService,
        cache_repository: RecommendationCacheRepository,
        user_repository: UserRepository,
    ):
        self.recommendation_service = recommendation_service
        self.cache_repository = cache_repository
        self.user_repository = user_repository

    async def execute(self) -> None:
        try:
            await self.cache_repository.delete_expired()

            users = await self.user_repository.find_all()

            for user in users:
                if user.id is None:
                    continue

                try:
                    await self.recommendation_service.get_recommendations(
                        user.id, limit=10
                    )
                except Exception:
                    pass

        except Exception as e:
            import logging

            logging.error(f"Failed to update recommendation cache: {e}")
