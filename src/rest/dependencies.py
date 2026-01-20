from config import get_config_from_toml
from infrastructure.repositories.codeforces import CodeforcesRepositoryImpl
from infrastructure.repositories.users import UserRepositoryImpl
from infrastructure.repositories.sessions import SessionRepository
from infrastructure.repositories.submissions import SubmissionRepositoryImpl
from infrastructure.repositories.problems import ProblemRepositoryImpl
from infrastructure.repositories.contests import ContestRepositoryImpl
from infrastructure.repositories.rating_changes import RatingChangeRepositoryImpl
from infrastructure.repositories.user_contest_participation import (
    UserContestParticipationRepositoryImpl,
)
from infrastructure.repositories.user_problem_status import (
    UserProblemStatusRepositoryImpl,
)
from infrastructure.repositories.user_problem_rating import (
    UserProblemRatingRepositoryImpl,
)
from infrastructure.repositories.recommendation_cache import (
    RecommendationCacheRepositoryImpl,
)
from infrastructure.repositories.user_preferences import (
    UserPreferencesRepositoryImpl,
)
from infrastructure.events.event_bus import EventBus
from domain.repositories.codeforces import CodeforcesRepository
from domain.repositories.users import UserRepository
from domain.repositories.submissions import SubmissionRepository
from domain.repositories.problems import ProblemRepository
from domain.repositories.contests import ContestRepository
from domain.repositories.rating_changes import RatingChangeRepository
from domain.repositories.user_contest_participation import (
    UserContestParticipationRepository,
)
from domain.repositories.user_problem_status import UserProblemStatusRepository
from domain.repositories.user_problem_rating import UserProblemRatingRepository
from domain.repositories.recommendation_cache import RecommendationCacheRepository
from domain.repositories.user_preferences import UserPreferencesRepository
from application.usecases.authenticate_user import AuthenticateUserUseCase
from application.services.recommendation_service import RecommendationService
from application.recommenders.content_based import ContentBasedRecommender
from application.recommenders.collaborative import CollaborativeFilteringRecommender
from application.recommenders.rating_based import RatingBasedRecommender
from application.recommenders.hybrid import HybridRecommender
from application.recommenders.matrix_factorization import MatrixFactorizationRecommender


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


_event_bus = None


def get_event_bus() -> EventBus:
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


_submission_repository = None


def get_submission_repository() -> SubmissionRepository:
    global _submission_repository
    if _submission_repository is None:
        config = get_config()
        _submission_repository = SubmissionRepositoryImpl(config.database.db_path_path)
    return _submission_repository


_problem_repository = None


def get_problem_repository() -> ProblemRepository:
    global _problem_repository
    if _problem_repository is None:
        config = get_config()
        _problem_repository = ProblemRepositoryImpl(config.database.db_path_path)
    return _problem_repository


_contest_repository = None


def get_contest_repository() -> ContestRepository:
    global _contest_repository
    if _contest_repository is None:
        config = get_config()
        _contest_repository = ContestRepositoryImpl(config.database.db_path_path)
    return _contest_repository


_rating_change_repository = None


def get_rating_change_repository() -> RatingChangeRepository:
    global _rating_change_repository
    if _rating_change_repository is None:
        config = get_config()
        _rating_change_repository = RatingChangeRepositoryImpl(
            config.database.db_path_path
        )
    return _rating_change_repository


_authenticate_user_usecase = None


def get_authenticate_user_usecase() -> AuthenticateUserUseCase:
    global _authenticate_user_usecase
    if _authenticate_user_usecase is None:
        _authenticate_user_usecase = AuthenticateUserUseCase(
            codeforces_repository=get_codeforces_repository(),
            user_repository=get_user_repository(),
            event_bus=get_event_bus(),
        )
    return _authenticate_user_usecase


_participation_repository = None


def get_participation_repository() -> UserContestParticipationRepository:
    global _participation_repository
    if _participation_repository is None:
        config = get_config()
        _participation_repository = UserContestParticipationRepositoryImpl(
            config.database.db_path_path
        )
    return _participation_repository


_problem_status_repository = None


def get_problem_status_repository() -> UserProblemStatusRepository:
    global _problem_status_repository
    if _problem_status_repository is None:
        config = get_config()
        _problem_status_repository = UserProblemStatusRepositoryImpl(
            config.database.db_path_path
        )
    return _problem_status_repository


_user_problem_rating_repository = None


def get_user_problem_rating_repository() -> UserProblemRatingRepository:
    global _user_problem_rating_repository
    if _user_problem_rating_repository is None:
        config = get_config()
        _user_problem_rating_repository = UserProblemRatingRepositoryImpl(
            config.database.db_path_path
        )
    return _user_problem_rating_repository


_recommendation_cache_repository = None


def get_recommendation_cache_repository() -> RecommendationCacheRepository:
    global _recommendation_cache_repository
    if _recommendation_cache_repository is None:
        config = get_config()
        _recommendation_cache_repository = RecommendationCacheRepositoryImpl(
            config.database.db_path_path
        )
    return _recommendation_cache_repository


_user_preferences_repository = None


def get_user_preferences_repository() -> UserPreferencesRepository:
    global _user_preferences_repository
    if _user_preferences_repository is None:
        config = get_config()
        _user_preferences_repository = UserPreferencesRepositoryImpl(
            config.database.db_path_path
        )
    return _user_preferences_repository


_recommendation_service = None


def get_recommendation_service() -> RecommendationService:
    global _recommendation_service
    if _recommendation_service is None:
        config = get_config()

        content_based = ContentBasedRecommender(
            user_problem_status_repository=get_problem_status_repository(),
            problem_repository=get_problem_repository(),
            user_repository=get_user_repository(),
            submission_repository=get_submission_repository(),
        )

        collaborative = CollaborativeFilteringRecommender(
            user_problem_status_repository=get_problem_status_repository(),
            user_repository=get_user_repository(),
            problem_repository=get_problem_repository(),
        )

        rating_based = RatingBasedRecommender(
            user_problem_rating_repository=get_user_problem_rating_repository(),
            user_problem_status_repository=get_problem_status_repository(),
            problem_repository=get_problem_repository(),
            user_repository=get_user_repository(),
        )

        hybrid = HybridRecommender(
            content_based=content_based,
            collaborative=collaborative,
        )

        matrix_factorization = MatrixFactorizationRecommender(
            user_problem_status_repository=get_problem_status_repository(),
            user_repository=get_user_repository(),
            problem_repository=get_problem_repository(),
        )

        recommenders = {
            "content_based": content_based,
            "collaborative": collaborative,
            "rating_based": rating_based,
            "hybrid": hybrid,
            "matrix_factorization": matrix_factorization,
        }

        _recommendation_service = RecommendationService(
            recommenders=recommenders,
            user_preferences_repository=get_user_preferences_repository(),
            cache_repository=get_recommendation_cache_repository(),
            cache_ttl_hours=config.recommendations.cache_ttl_hours,
        )
    return _recommendation_service
