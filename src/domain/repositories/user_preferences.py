from abc import ABC, abstractmethod
from typing import Optional
from domain.models.user_preferences import UserPreferences


class UserPreferencesRepository(ABC):
    @abstractmethod
    async def find_by_user_id(self, user_id: int) -> Optional[UserPreferences]:
        pass

    @abstractmethod
    async def create(self, preferences: UserPreferences) -> UserPreferences:
        pass

    @abstractmethod
    async def update(self, preferences: UserPreferences) -> UserPreferences:
        pass
