from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.database.models.user_model import UserModel
from src.infrastructure.database.mappers.user_mapper import UserMapper

class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None

    async def find_by_email(self, email: str) -> Optional[User]:
        # Eu busco pelo email padronizado em caixa baixa
        stmt = select(UserModel).where(UserModel.email == email.strip().lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserMapper.to_domain(model) if model else None

    async def save(self, user: User) -> None:
        stmt = insert(UserModel).values(
            id=user.id,
            email=user.email,
            hashed_password=user.hashed_password,
            created_at=user.created_at,
        )

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[UserModel.email],
            set_={"hashed_password": stmt.excluded.hashed_password}
        )
        await self._session.execute(upsert_stmt)