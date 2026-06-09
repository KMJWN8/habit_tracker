from uuid import UUID
from datetime import datetime, time
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HabitBase(BaseModel):
    """Базовая схема привычки с общими полями."""
    
    title: Annotated[
        str,
        Field(
            ...,
            min_length=1,
            max_length=100,
            description="Название привычки",
            examples=["Утренняя пробежка", "Читать 30 минут", "Медитация"],
        )
    ]
    
    description: Annotated[
        str | None,
        Field(
            None,
            max_length=500,
            description="Подробное описание привычки и её цели",
            examples=["Бегать в парке 5 км каждое утро перед работой"],
        )
    ]
    
    color: Annotated[
        str,
        Field(
            default="#3B82F6",
            pattern="^#[0-9A-Fa-f]{6}$",
            description="Цвет привычки в HEX формате (#RRGGBB)",
            examples=["#3B82F6", "#EF4444", "#10B981"],
        )
    ]
    
    goal_streak: Annotated[
        int,
        Field(
            default=21,
            ge=1,
            le=365,
            description="Целевое количество дней подряд для формирования привычки",
            examples=[21, 30, 66],
        )
    ]
    
    reminder_time: Annotated[
        time | None,
        Field(
            None,
            description="Время ежедневного напоминания в формате HH:MM:SS",
            examples=["08:00:00", "21:30:00"],
        )
    ]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Утренняя пробежка",
                    "description": "Бегать в парке 5 км каждое утро перед работой",
                    "color": "#3B82F6",
                    "goal_streak": 30,
                    "reminder_time": "07:00:00",
                }
            ]
        }
    }


class HabitCreate(HabitBase):
    """Схема для создания новой привычки."""
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Медитация",
                    "description": "10 минут mindfulness медитации после пробуждения",
                    "color": "#8B5CF6",
                    "goal_streak": 21,
                    "reminder_time": "06:30:00",
                }
            ]
        }
    }


class HabitUpdate(BaseModel):
    """
    Схема для частичного обновления привычки.
    Передавайте только те поля, которые нужно изменить.
    """
    
    title: Annotated[
        str | None,
        Field(
            None,
            min_length=1,
            max_length=100,
            description="Новое название привычки",
            examples=["Вечерняя пробежка"],
        )
    ]
    
    description: Annotated[
        str | None,
        Field(
            None,
            max_length=500,
            description="Новое описание привычки",
            examples=["Бегать 3 км вечером для снятия стресса"],
        )
    ]
    
    color: Annotated[
        str | None,
        Field(
            None,
            pattern="^#[0-9A-Fa-f]{6}$",
            description="Новый цвет в HEX формате",
            examples=["#EF4444"],
        )
    ]
    
    goal_streak: Annotated[
        int | None,
        Field(
            None,
            ge=1,
            le=365,
            description="Новая цель по дням подряд",
            examples=[66],
        )
    ]
    
    reminder_time: Annotated[
        time | None,
        Field(
            None,
            description="Новое время напоминания",
            examples=["19:00:00"],
        )
    ]
    
    is_active: Annotated[
        bool | None,
        Field(
            None,
            description="Статус активности привычки",
            examples=[True, False],
        )
    ]

    @field_validator("color", mode="before")
    @classmethod
    def validate_and_normalize_color(cls, v: str | None) -> str | None:
        """
        Валидация и нормализация цвета:
        - Добавляет # если отсутствует
        - Приводит к верхнему регистру
        - Убирает пробелы
        """
        if v is None:
            return None
        
        if not isinstance(v, str):
            return v
        
        # Нормализация: убираем пробелы и приводим к верхнему регистру
        v = v.strip().upper()
        
        # Добавляем # если отсутствует
        if not v.startswith('#'):
            v = f"#{v}"
        
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Вечерняя медитация",
                    "color": "#10B981",
                    "reminder_time": "21:00:00",
                }
            ]
        }
    }


class HabitResponse(HabitBase):
    """Полная информация о привычке с системными полями."""
    
    id: Annotated[
        int,
        Field(
            ...,
            description="Уникальный идентификатор привычки",
            examples=[42, 123],
        )
    ]
    
    user_id: Annotated[
        UUID,
        Field(
            ...,
            description="ID пользователя, которому принадлежит привычка",
            examples=["550e8400-e29b-41d4-a716-446655440000"],
        )
    ]
    
    is_active: Annotated[
        bool,
        Field(
            True,
            description="Активна ли привычка (False для soft-deleted)",
            examples=[True],
        )
    ]
    
    created_at: Annotated[
        datetime,
        Field(
            ...,
            description="Дата и время создания привычки (ISO 8601)",
            examples=["2026-06-09T10:30:00.123456"],
        )
    ]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 42,
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "title": "Утренняя пробежка",
                    "description": "Бегать в парке 5 км каждое утро",
                    "color": "#3B82F6",
                    "goal_streak": 30,
                    "reminder_time": "07:00:00",
                    "is_active": True,
                    "created_at": "2026-06-09T07:00:00.123456",
                }
            ]
        },
    )