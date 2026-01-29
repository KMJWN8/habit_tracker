from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Atomic Habits Tracker API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    API_URL_PREFIX: str = "http://localhost:8000"
    
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True

    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    ALLOWED_HOSTS: list[str] = ["*"]

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    #server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int


    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env'
    )

settings = Settings()