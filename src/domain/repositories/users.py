from abc import ABC, abstractmethod

from domain.models.user import User


class UserRepository(ABC):
    @abstractmethod
    async def find_by_external_id(self, external_id: str) -> User | None:
        pass

    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def update(self, user: User) -> User:
        pass

    @abstractmethod
    async def find_by_id(self, user_id: int) -> User | None:
        pass
