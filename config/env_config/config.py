from pydantic import SecretStr, Field, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


class MayakConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='mayak_')

    login: str
    password: SecretStr


class DatabaseConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='db_')

    filename: str


class EmailConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='email_')

    smtp_login: EmailStr
    smtp_password: SecretStr
    smtp_server: str
    smtp_port: int = 465
    target_emails: list[EmailStr]


class StorageConfig(BaseConfig):
    model_config = SettingsConfigDict(env_prefix='storage_')

    folder_path: str


class Config(BaseConfig):
    mayak_config: MayakConfig = Field(default_factory=MayakConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)
    storage: StorageConfig = Field(default_factory=StorageConfig)
    debug: bool = False

    @classmethod
    def load(cls) -> 'Config':
        return cls()
