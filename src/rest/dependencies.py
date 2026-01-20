from config import get_config_from_toml
from infrastructure.repositories.codeforces import CodeforcesRepositoryImpl
from infrastructure.repositories.users import UserRepositoryImpl
from infrastructure.repositories.sessions import SessionRepository
from domain.repositories.codeforces import CodeforcesRepository
from domain.repositories.users import UserRepository


_config = None


def get_config():
    global _config
    if _config is None:
        _config = get_config_from_toml()
    return _config


_codeforces_repository = None


def get_codeforces_repository() -> CodeforcesRepository:
    global _codeforces_repository
    if _codeforces_repository is None:
        config = get_config()
        _codeforces_repository = CodeforcesRepositoryImpl(
            issuer=config.codeforces.issuer,
            client_id=config.codeforces.client_id,
            client_secret=config.codeforces.client_secret,
            redirect_uri=config.codeforces.redirect_uri,
        )
    return _codeforces_repository


_user_repository = None


def get_user_repository() -> UserRepository:
    global _user_repository
    if _user_repository is None:
        config = get_config()
        _user_repository = UserRepositoryImpl(config.database.db_path_path)
    return _user_repository


_session_repository = None


def get_session_repository() -> SessionRepository:
    global _session_repository
    if _session_repository is None:
        config = get_config()
        _session_repository = SessionRepository(config.session.secret_key)
    return _session_repository
