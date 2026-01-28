from fastapi import APIRouter
from app.api.v1.endpoints import auth, habits, analytics


api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth.router)
api_v1_router.include_router(habits.router)
api_v1_router.include_router(analytics.router)
