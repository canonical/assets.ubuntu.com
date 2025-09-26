from pydantic import AliasChoices, SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILES = (".env", ".env.local")


class SwiftConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES, extra="ignore", env_prefix="flask_os_"
    )
    auth_url: str
    username: str
    password: SecretStr
    auth_version: str
    tenant_name: str = ""


class DirectoryApiConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES, extra="ignore", env_prefix="flask_directory_api_"
    )
    url: str
    token: SecretStr

# Salesforce Trino Config
class TrinoSFConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES, extra="ignore", env_prefix="flask_trino_sf_"
    )
    type: str = "service_account"
    universe_domain: str = "googleapis.com"
    project_id: str
    private_key_id: str
    private_key: str
    client_email: str
    client_id: str
    auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    token_uri: str = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url: str = (
        "https://www.googleapis.com/oauth2/v1/certs"
    )


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILES, extra="ignore", env_prefix="flask_"
    )

    secret_key: SecretStr
    read_only_mode: bool = False
    database_url: SecretStr = Field(
        validation_alias=AliasChoices(
            "database_url",
            "postgresql_db_connect_string",
        )
    )
    swift: SwiftConfig = SwiftConfig()  # type: ignore
    directory_api: DirectoryApiConfig = DirectoryApiConfig()  # type: ignore
    trino_sf: TrinoSFConfig = TrinoSFConfig()  # type: ignore


config = Config()  # type: ignore
