from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from app.schemas.habit import (
    HabitCreate,
    HabitUpdate,
    HabitResponse
)


router = APIRouter(prefix="/habits", tags=["habits"])