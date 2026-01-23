from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from app.api.v1.endpoints.habits import router as habits_router
from app.core.logger import get_logger

logger = get_logger(__name__)

logger.info("Application started")

app = FastAPI(title="Atomic Habits Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.include_router(habits_router)
