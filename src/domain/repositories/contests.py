from abc import ABC, abstractmethod
from typing import Optional
from domain.models.contest import Contest


class ContestRepository(ABC):
    @abstractmethod
    async def find_by_contest_id(self, contest_id: int) -> Optional[Contest]:
        pass

    @abstractmethod
    async def create(self, contest: Contest) -> Contest:
        pass

    @abstractmethod
    async def create_many(self, contests: list[Contest]) -> None:
        pass

    @abstractmethod
    async def find_all(self) -> list[Contest]:
        pass
