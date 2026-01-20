from abc import ABC, abstractmethod
from typing import Optional
from domain.models.recommendation_cache import RecommendationCache


class RecommendationCacheRepository(ABC):
    @abstractmethod
    async def find_by_user_and_type(
        self, user_id: int, recommender_type: str
    ) -> Optional[RecommendationCache]:
        pass

    @abstractmethod
    async def create(self, cache: RecommendationCache) -> RecommendationCache:
        pass

    @abstractmethod
    async def update(self, cache: RecommendationCache) -> RecommendationCache:
        pass

    @abstractmethod
    async def delete_expired(self) -> None:
        pass

    @abstractmethod
    async def delete_by_user_and_type(
        self, user_id: int, recommender_type: str
    ) -> None:
        pass
