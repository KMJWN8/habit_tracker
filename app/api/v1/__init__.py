from fastapi import APIRouter
from app.api.v1.endpoints import auth, habit, analytics


api_v1_router = APIRouter()

api_v1_router.include_router(auth.router)
api_v1_router.include_router(habit.router)
api_v1_router.include_router(analytics.router)
