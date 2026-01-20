from abc import ABC, abstractmethod
from typing import Optional
from domain.models.problem import Problem


class ProblemRepository(ABC):
    @abstractmethod
    async def find_by_contest_and_index(
        self, contest_id: int, problem_index: str
    ) -> Optional[Problem]:
        pass

    @abstractmethod
    async def create(self, problem: Problem) -> Problem:
        pass

    @abstractmethod
    async def create_many(self, problems: list[Problem]) -> None:
        pass

    @abstractmethod
    async def find_by_contest_id(self, contest_id: int) -> list[Problem]:
        pass
