from typing import Any, Generic, Optional, Type, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger

logger = get_logger(__name__)


ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, data: dict[str, Any]) -> ModelType:
        try:
            db_obj = self.model(**data)

            self.session.add(db_obj)
            await self.session.commit()
            await self.session.refresh(db_obj)

            logger.info(f"Создана запись {self.model.__name__} с id: {db_obj.id}")
            return db_obj
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка создания: {str(e)}")
            raise

    async def get(self, id: int) -> Optional[ModelType]:
        try:
            query = select(self.model).where(self.model.id == id)
            result = await self.session.execute(query)
            obj = result.scalar_one_or_none()

            if obj:
                logger.debug(f"Найдена запись {self.model.__name__} с id {id}")
            else:
                logger.debug(f"Запись {self.model.__name__} с id {id} не найдена")

            return obj
        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения записи {id}: {str(e)}")
            raise

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        try:
            query = select(self.model).offset(skip).limit(limit)
            result = await self.session.execute(query)
            return list(result.scalars.all())

        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения всех записей: {str(e)}")
            raise

    async def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        try:
            if not hasattr(self.model, field_name):
                raise AttributeError(
                    f"Поле не {field_name} существует в {self.model.__name__}"
                )
            query = select(self.model).where(getattr(self.model, field_name) == value)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения по полю {field_name}: {str(e)}")
            raise

    async def update(self, id: int, data: dict[str, Any]) -> Optional[ModelType]:
        try:
            # Убираем значения None (они не обновляются)
            update_data = {k: v for k, v in data.items() if v is not None}

            if not update_data:
                return await self.get(id)

            query = (
                update(self.model)
                .where(self.model.id == id)
                .values(**update_data)
                .returning(self.model)
            )

            result = await self.session.execute(query)
            updated_obj = result.scalar_one_or_none()

            if updated_obj:
                await self.session.commit()
                await self.session.refresh(updated_obj)
                logger.info(f"Обновлен {self.model.__name__} с id: {id}")
                return updated_obj
            else:
                await self.session.rollback()
                logger.warning(f"{self.model.__name__} с id не найден")
                return None
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка обновления {self.model.__name__} {id}: {str(e)}")
            raise

    async def delete(self, id: int) -> bool:
        try:
            obj = await self.get(id)
            if not obj:
                logger.warning(f"{self.model.__name__} с id {id} не найден")
                return False

            query = delete(self.model).where(self.model.id == id)
            await self.session.execute(query)
            await self.session.commit()

            logger.info(f"Удален {self.model.__name__} c id: {id}")
            return True
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка удаления {self.model.__name__} {id}: {str(e)}")
            raise
