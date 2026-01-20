from abc import ABC, abstractmethod
from typing import Optional
from domain.models.user_problem_rating import UserProblemRating


class UserProblemRatingRepository(ABC):
    @abstractmethod
    async def find_by_user_and_problem(
        self, user_id: int, contest_id: Optional[int], problem_index: Optional[str]
    ) -> Optional[UserProblemRating]:
        pass

    @abstractmethod
    async def create(self, rating: UserProblemRating) -> UserProblemRating:
        pass

    @abstractmethod
    async def update(self, rating: UserProblemRating) -> UserProblemRating:
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: int) -> list[UserProblemRating]:
        pass

    @abstractmethod
    async def find_by_problem(
        self, contest_id: Optional[int], problem_index: Optional[str]
    ) -> list[UserProblemRating]:
        pass
