from pathlib import Path
from toml import load as load_toml
from pydantic import BaseModel, HttpUrl, SecretStr


class CodeforcesConfig(BaseModel):
    issuer: HttpUrl
    client_id: str
    redirect_uri: HttpUrl
    client_secret: SecretStr


class SessionConfig(BaseModel):
    secret_key: SecretStr


class DatabaseConfig(BaseModel):
    db_path: str

    @property
    def db_path_path(self) -> Path:
        return Path(self.db_path)


class JobConfig(BaseModel):
    sync_interval_hours: float


class Config(BaseModel):
    codeforces: CodeforcesConfig
    session: SessionConfig
    database: DatabaseConfig
    jobs: JobConfig


def get_config_from_toml(path: Path = Path("config.toml")) -> Config:
    return Config(**load_toml(path))
