from abc import ABC, abstractmethod
from typing import Optional
from domain.models.rating_change import RatingChange


class RatingChangeRepository(ABC):
    @abstractmethod
    async def find_by_user_and_contest(
        self, user_id: int, contest_id: int
    ) -> Optional[RatingChange]:
        pass

    @abstractmethod
    async def create(self, rating_change: RatingChange) -> RatingChange:
        pass

    @abstractmethod
    async def create_many(self, rating_changes: list[RatingChange]) -> None:
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: int) -> list[RatingChange]:
        pass

    @abstractmethod
    async def find_latest_by_user_id(
        self, user_id: int, limit: int = 1
    ) -> list[RatingChange]:
        pass
