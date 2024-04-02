from functools import lru_cache
import os

# from dotenv import load_dotenv
from google.oauth2.service_account import Credentials

from langchain_google_vertexai import VertexAIEmbeddings
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# load_dotenv()
# key_path = os.environ["GCLOUD_SERVICE_ACCOUNT_KEY_PATH"]
# credentials = Credentials.from_service_account_file(key_path, scopes=["https://www.googleapis.com/auth/cloud-platform"])
# # PROJECT_ID = os.environ["PROJECT_ID"]


class Path:
    app_dir: str = os.path.dirname(os.path.abspath(__file__))
    root_dir: str = os.path.dirname(app_dir)
    secrets_dir: str = os.path.join(root_dir, "secrets")
    env_file: str = os.path.join(app_dir, ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path.env_file, extra="ignore")

    GCLOUD_SERVICE_ACCOUNT_KEY_PATH: str = Field()
    PROJECT_ID: str = Field()


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

# print(config.model_dump(), creds)
# print(os.path.join(Path.secrets_dir, config.GCLOUD_SERVICE_ACCOUNT_KEY_PATH))


# v = VertexAIEmbeddings(
#     model_name="textembedding-gecko@003",
#     project=config.PROJECT_ID,
#     location="us-central1",
#     credentials=creds,
# )
# print(v.embed_query("Hello World"))
