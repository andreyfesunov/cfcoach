from abc import ABC, abstractmethod
from typing import Optional
from domain.models.user_contest_participation import UserContestParticipation


class UserContestParticipationRepository(ABC):
    @abstractmethod
    async def find_by_user_and_contest(
        self, user_id: int, contest_id: int
    ) -> Optional[UserContestParticipation]:
        pass

    @abstractmethod
    async def create(
        self, participation: UserContestParticipation
    ) -> UserContestParticipation:
        pass

    @abstractmethod
    async def update(
        self, participation: UserContestParticipation
    ) -> UserContestParticipation:
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: int) -> list[UserContestParticipation]:
        pass

    @abstractmethod
    async def find_by_contest_id(
        self, contest_id: int
    ) -> list[UserContestParticipation]:
        pass
