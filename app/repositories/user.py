from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import get_logger
from app.core.exceptions import NotFoundError, DatabaseError
from app.models.user import User

logger = get_logger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.model = User

    async def get(self, id: UUID) -> User | None:
        try:
            query = select(self.model).where(self.model.id == id)
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()
            if not user:
                raise NotFoundError("User")
            return user
        
        except SQLAlchemyError as e:
            logger.error("Failed to get user | user_id=%s | error=%s", id, e)
            raise DatabaseError("Failed to get user") from e
        
    async def get_by_email(self, email: str) -> User | None:
        try:
            query = select(self.model).where(self.model.email == email)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            logger.error("Failed to get user by email | email=%s | error=%s", email, e)
            raise DatabaseError("Failed to get user by email") from e

    async def get_by_username(self, username: str) -> User | None:
        try: 
            query = select(self.model).where(self.model.username == username)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        
        except SQLAlchemyError as e:
            logger.error("Failed to get user by username | username=%s | error=%s", username, e)
            raise DatabaseError("Failed to get user by username") from e
        
    async def create(self, data: dict) -> User:
        try:
            user = self.model(**data)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

            logger.info("User created | user_id=%s", user.id)
            return user
        
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error("Failed to create user | error=%s", e)
            raise DatabaseError("Failed to create user") from e

    async def update(self, id: UUID, data: dict) -> User:
        user = await self.get(id)

        try:
            for key, value in data.items():
                setattr(user, key, value)

            await self.session.commit()
            await self.session.refresh(user)

            logger.info("User updated | user_id=%s", id)
            return user
        
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error("Failed to update user | user_id=%s | error=%s", id, e)
            raise DatabaseError("Failed to update user") from e

    async def delete(self, id: UUID) -> bool:
        user = await self.get(id)

        try:
            await self.session.delete(user)
            await self.session.commit()

            logger.info("User deleted | user_id=%s", id)
            return True
        
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error("Failed to delete user | user_id=%s | error=%s", id, e)
            raise DatabaseError("Failed to delete user") from e

    async def exists(self, id: UUID) -> bool:
        try:
            query = select(self.model.id).where(self.model.id == id)
            result = await self.session.execute(query)
            return result.scalar_one_or_none() is not None

        except SQLAlchemyError as e:
            logger.error("Failed to check user existence | user_id=%s | error=%s", id, e)
            raise DatabaseError("Failed to check user existence") from e
