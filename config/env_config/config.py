from pydantic import SecretStr
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

    @classmethod
    def load(cls) -> 'MayakConfig':
        return cls()
