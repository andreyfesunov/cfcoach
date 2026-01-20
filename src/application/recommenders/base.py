from abc import ABC, abstractmethod
from typing import TypedDict


class RecommendationResult(TypedDict):
    problem_id: int
    contest_id: int | None
    problem_index: str | None
    score: float


class Recommender(ABC):
    @abstractmethod
    async def recommend(
        self, user_id: int, limit: int = 10
    ) -> list[RecommendationResult]:
        pass

    @abstractmethod
    def get_type(self) -> str:
        pass

    @abstractmethod
    async def needs_training(self) -> bool:
        pass

    @abstractmethod
    async def train(self) -> None:
        pass
