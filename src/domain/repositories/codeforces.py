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
