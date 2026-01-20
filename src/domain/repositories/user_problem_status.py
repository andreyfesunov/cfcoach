from abc import ABC, abstractmethod
from typing import Optional
from domain.models.user_problem_status import UserProblemStatus


class UserProblemStatusRepository(ABC):
    @abstractmethod
    async def find_by_user_and_problem(
        self, user_id: int, contest_id: Optional[int], problem_index: Optional[str]
    ) -> Optional[UserProblemStatus]:
        pass

    @abstractmethod
    async def create(self, status: UserProblemStatus) -> UserProblemStatus:
        pass

    @abstractmethod
    async def update(self, status: UserProblemStatus) -> UserProblemStatus:
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: int) -> list[UserProblemStatus]:
        pass

    @abstractmethod
    async def find_solved_by_user_id(self, user_id: int) -> list[UserProblemStatus]:
        pass

    @abstractmethod
    async def find_unsolved_by_user_id(self, user_id: int) -> list[UserProblemStatus]:
        pass
