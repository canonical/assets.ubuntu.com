from pydantic import AliasChoices, SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILES = (".env", ".env.local")


class SwiftConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES, extra="ignore", env_prefix="os_"
    )
    auth_url: str
    username: str
    password: SecretStr
    auth_version: str
    tenant_name: str = ""


class DirectoryApiConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES, extra="ignore", env_prefix="directory_api_"
    )
    url: str
    token: SecretStr


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILES, extra="ignore")

    secret_key: SecretStr
    database_url: SecretStr = Field(
        validation_alias=AliasChoices(
            "database_url",
            "postgresql_db_connect_string",
        )
    )
    swift: SwiftConfig = SwiftConfig()  # type: ignore
    directory_api: DirectoryApiConfig = DirectoryApiConfig()  # type: ignore


config = Config()  # type: ignore
