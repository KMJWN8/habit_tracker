from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.logger import get_logger


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Здесь можно добавить инициализацию подключений к БД, кэшу и т.д.
    # Например: await database.connect()

    yield

    logger.info("Shutting down application...")

    # Здесь можно добавить закрытие подключений
    # Например: await database.disconnect()

#app = FastAPI(title="Atomic Habits Tracker API")

def create_application() -> FastAPI:
    openapi_tags = [
        {
            "name": "auth",
            "description": "Аутентификация и авторизация",
        },
        {
            "name": "habits",
            "description": "Операции с привычками",
        },
    ]

    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="Atomic Habits Tracker API",
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json" if settings.ENVIRONMENT != "production" else None,
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
        openapi_tags=openapi_tags,
    )

    setup_middleware(application)

    setup_routers(application)

    return application


def setup_middleware(application: FastAPI) -> None:
    # CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # TrustedHost middleware для production
    if settings.ENVIRONMENT == "production":
        application.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )


def setup_routers(application: FastAPI) -> None:
    """
    Подключение всех роутеров приложения.
    """
    # Основной API v1 роутер
    application.include_router(
        api_v1_router,
        prefix=settings.API_V1_STR,
    )
    
    
    # Root endpoint
    @application.get("/", tags=["root"])
    async def root():
        """Корневой endpoint с информацией об API."""
        return {
            "message": f"Welcome to {settings.PROJECT_NAME} API",
            "version": settings.VERSION,
            "docs": "/docs",
            "api_v1": settings.API_V1_STR,
        }


app = create_application()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info" if settings.ENVIRONMENT == "production" else "debug",
    )