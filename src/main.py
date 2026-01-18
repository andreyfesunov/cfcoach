from config import get_config_from_toml
from infrastructure.repositories.codeforces import CodeforcesRepository

config = get_config_from_toml()
codeforces_repository = CodeforcesRepository(
    issuer=config.codeforces.issuer,
    client_id=config.codeforces.client_id,
    client_secret=config.codeforces.client_secret,
    redirect_uri=config.codeforces.redirect_uri,
)

print(codeforces_repository.get_auth_url())
