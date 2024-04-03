import os
from functools import lru_cache

from google.oauth2.service_account import Credentials
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Path:
    app_dir: str = os.path.dirname(os.path.abspath(__file__))
    root_dir: str = os.path.dirname(app_dir)
    secrets_dir: str = os.path.join(root_dir, "secrets")
    env_file: str = os.path.join(app_dir, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path.env_file, extra="ignore")

    GCLOUD_SERVICE_ACCOUNT_KEY_PATH: str = Field()
    PROJECT_ID: str = Field()
    PROJECT_LOCATION: str = Field()

    CREDENTIALS: Credentials | None = Field(default=None)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.CREDENTIALS = Credentials.from_service_account_file(
        os.path.join(Path.secrets_dir, settings.GCLOUD_SERVICE_ACCOUNT_KEY_PATH),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )
    return settings


config = get_settings()
