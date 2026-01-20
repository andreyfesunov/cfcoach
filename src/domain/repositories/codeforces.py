from abc import ABC, abstractmethod

from pydantic import HttpUrl


class CodeforcesRepository(ABC):
    @abstractmethod
    def get_auth_url(self) -> HttpUrl:
        pass

    @abstractmethod
    def exchange_code_for_tokens(self, code: str, state: str | None = None) -> dict:
        pass

    @abstractmethod
    def get_user_info(self, access_token: str, id_token: str | None = None) -> dict:
        pass

    @abstractmethod
    def get_user_submissions(
        self, handle: str, access_token: str, from_index: int = 1, count: int = 1000
    ) -> list[dict]:
        pass

    @abstractmethod
    def get_user_rating(self, handle: str, access_token: str) -> list[dict]:
        pass

    @abstractmethod
    def get_contest_list(self, gym: bool = False) -> list[dict]:
        pass

    @abstractmethod
    def get_problem_set(self) -> list[dict]:
        pass
