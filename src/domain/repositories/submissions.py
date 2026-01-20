from abc import ABC, abstractmethod
from typing import Optional
from domain.models.submission import Submission


class SubmissionRepository(ABC):
    @abstractmethod
    async def find_by_submission_id(self, submission_id: int) -> Optional[Submission]:
        pass

    @abstractmethod
    async def create(self, submission: Submission) -> Submission:
        pass

    @abstractmethod
    async def create_many(self, submissions: list[Submission]) -> None:
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: int) -> list[Submission]:
        pass

    @abstractmethod
    async def find_latest_by_user_id(
        self, user_id: int, limit: int = 1
    ) -> list[Submission]:
        pass
