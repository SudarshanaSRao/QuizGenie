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


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings


config = get_settings()


def get_credentials():
    return Credentials.from_service_account_file(
        os.path.join(Path.secrets_dir, config.GCLOUD_SERVICE_ACCOUNT_KEY_PATH),
        scopes=["https://www.googleapis.com/auth/cloud-platform"],
    )


creds = get_credentials()
