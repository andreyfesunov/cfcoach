from domain.repositories.codeforces import CodeforcesRepository
from domain.repositories.users import UserRepository
from domain.models.user import User
from domain.events.user_authenticated import UserAuthenticatedEvent
from infrastructure.events.event_bus import EventBus


class AuthenticateUserUseCase:
    def __init__(
        self,
        codeforces_repository: CodeforcesRepository,
        user_repository: UserRepository,
        event_bus: EventBus,
    ):
        self.codeforces_repository = codeforces_repository
        self.user_repository = user_repository
        self.event_bus = event_bus

    async def execute(self, code: str, state: str | None = None) -> User:
        token_response = self.codeforces_repository.exchange_code_for_tokens(
            code, state
        )

        if not token_response or "access_token" not in token_response:
            raise ValueError(f"Token response missing access_token: {token_response}")

        access_token = token_response["access_token"]
        id_token = token_response.get("id_token")

        user_info = self.codeforces_repository.get_user_info(access_token, id_token)

        external_user_id = (
            user_info.get("sub") or user_info.get("id") or user_info.get("handle")
        )

        if not external_user_id:
            raise ValueError("User ID not found in response")

        username = (
            user_info.get("handle")
            or user_info.get("preferred_username")
            or user_info.get("username")
        )

        user = await self.user_repository.find_by_external_id(external_user_id)

        if not user:
            user = User(
                external_id=external_user_id,
                username=username,
                access_token=access_token,
            )
            user = await self.user_repository.create(user)
        else:
            if username:
                user.username = username
            user.access_token = access_token
            user = await self.user_repository.update(user)

        if user.id is None:
            raise ValueError("User ID is not set")

        event = UserAuthenticatedEvent(
            user_id=user.id,
            external_id=user.external_id,
            username=user.username,
            access_token=access_token,
        )
        self.event_bus.publish(event)

        return user
