from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from app.models.tracking import HabitStatus


class HabitTrackingBase(BaseModel):
    """Базовая схема трекинга привычки с общими полями."""
    
    habit_id: Annotated[
        int,
        Field(
            ...,
            gt=0,
            description="ID привычки, к которой относится запись трекинга",
            examples=[42, 123],
        )
    ]
    
    date: Annotated[
        date,
        Field(
            ...,
            description="Дата выполнения привычки (формат: ГГГГ-ММ-ДД)",
            examples=["2026-06-09", "2026-01-15"],
        )
    ]
    
    status: Annotated[
        HabitStatus,
        Field(
            default=HabitStatus.COMPLETED,
            description="Статус выполнения: completed, skipped, missed",
            examples=["completed", "skipped", "missed"],
        )
    ]
    
    notes: Annotated[
        str | None,
        Field(
            None,
            max_length=500,
            description="Заметки о выполнении (опционально)",
            examples=["Пробежал 5 км за 25 минут", "Пропустил из-за болезни"],
        )
    ]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "habit_id": 42,
                    "date": "2026-06-09",
                    "status": "completed",
                    "notes": "Пробежал 5 км за 25 минут, отличный темп!",
                }
            ]
        }
    }


class HabitTrackingCreate(HabitTrackingBase):
    """Схема для создания новой записи трекинга."""
    
    # id и created_at исключены — их генерирует БД
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "habit_id": 42,
                    "date": "2026-06-09",
                    "status": "completed",
                    "notes": "Утренняя пробежка в парке",
                },
                {
                    "habit_id": 42,
                    "date": "2026-06-10",
                    "status": "skipped",
                    "notes": "Пропустил из-за дождя",
                },
            ]
        }
    }


class HabitTrackingUpdate(BaseModel):
    """
    Схема для частичного обновления записи трекинга.
    Передавайте только те поля, которые нужно изменить.
    """
    
    status: Annotated[
        HabitStatus | None,
        Field(
            None,
            description="Новый статус выполнения",
            examples=["completed", "skipped", "missed"],
        )
    ]
    
    notes: Annotated[
        str | None,
        Field(
            None,
            max_length=500,
            description="Обновленные заметки",
            examples=["Обновленная заметка о выполнении"],
        )
    ]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "completed",
                    "notes": "Фактически выполнил, хотя планировал пропустить",
                }
            ]
        }
    }


class HabitTrackingResponse(HabitTrackingBase):
    """Полная информация о записи трекинга с системными полями."""
    
    id: Annotated[
        int,
        Field(
            ...,
            description="Уникальный идентификатор записи трекинга",
            examples=[1001, 2045],
        )
    ]
    
    created_at: Annotated[
        datetime,
        Field(
            ...,
            description="Дата и время создания записи (ISO 8601)",
            examples=["2026-06-09T07:30:00.123456"],
        )
    ]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1001,
                    "habit_id": 42,
                    "date": "2026-06-09",
                    "status": "completed",
                    "notes": "Пробежал 5 км за 25 минут",
                    "created_at": "2026-06-09T07:30:00.123456",
                }
            ]
        },
    )