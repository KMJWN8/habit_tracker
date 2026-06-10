from pathlib import Path
from typing import Literal
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent

settings_config = SettingsConfigDict(
    env_file=BASE_DIR / ".env",
    env_file_encoding="utf-8",
    extra="ignore",
    populate_by_name=True,  # Позволяет использовать alias при загрузке из env
)


class DbSettings(BaseSettings):
    HOST: str = Field(alias="DB_HOST")
    PORT: str = Field(alias="DB_PORT")
    USER: str = Field(alias="DB_USER")
    PASS: str = Field(alias="DB_PASS")
    NAME: str = Field(alias="DB_NAME")

    model_config = settings_config

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.USER}:{self.PASS}@{self.HOST}:{self.PORT}/{self.NAME}"


class AuthSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    model_config = settings_config


class Settings(BaseSettings):
    # Общие настройки проекта
    PROJECT_NAME: str = "Atomic Habits Tracker"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    API_URL_PREFIX: str = "http://localhost:8000"
    
    # Окружение
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = True
    
    # Безопасность сети
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    ALLOWED_HOSTS: list[str] = ["*"]

    # Сетевые настройки сервера uvicorn
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    db: DbSettings = Field(default_factory=DbSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)

    model_config = settings_config


settings = Settings()
