from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate, UserUpdate

logger = get_logger(__name__)


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get(self, id: UUID) -> Optional[User]:
        try:
            query = select(self.model).where(self.model.id == id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()

        except (ValueError, AttributeError) as e:
            logger.error(f"Некорректный UUID: {id}: {str(e)}")
            return None
        except SQLAlchemyError as e:
            logger.error(f"Ошибка БД при получении пользователя {id}: {str(e)}")
            raise

    async def update(
        self, 
        id: UUID, 
        data: Dict[str, Any]
    ) -> Optional[User]:
        try:
            update_data = {k: v for k, v in data.items() if v is not None}
            if not update_data:
                return await self.get(id)

            query = (
                update(self.model)
                .where(self.model.id == id)
                .values(**update_data)
                .returning(self.model)
            )
            updated_user = self.session.execute(query)

            if updated_user:
                await self.session.commit()
                await self.session.refresh(updated_user)
            else:
                await self.session.rollback()
                return None

        except (ValueError, AttributeError) as e:
            logger.error(f"Некорректный UUID: {id}: {str(e)}")
            return None
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка обновления пользователя {id}: {str(e)}")
            raise

    async def delete(self, id: UUID) -> bool:
        try:
            user = await self.get(id)
            if not user:
                return False

            query = delete(User).where(User.id == id)
            await self.session.execute(query)
            await self.session.commit()

            return True

        except (ValueError, AttributeError) as e:
            logger.error(f"Некорректный UUID: {id}")
            return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка удаления пользователя {id}: {str(e)}")
            raise

    async def get_by_email(self, email: str) -> Optional[User]:
        return await self.get_by_field("email", email)

    async def get_by_username(self, username: str) -> Optional[User]:
        return await self.get_by_field("username", username)

    async def exists(self, id: UUID) -> bool:
        user = await self.get(id)
        return user is not None
