from pathlib import Path
from toml import load as load_toml
from pydantic import BaseModel, HttpUrl, SecretStr


class CodeforcesConfig(BaseModel):
    issuer: HttpUrl
    client_id: str
    redirect_uri: HttpUrl
    client_secret: SecretStr


class Config(BaseModel):
    codeforces: CodeforcesConfig


def get_config_from_toml(path: Path = Path("config.toml")) -> Config:
    return Config(**load_toml(path))
