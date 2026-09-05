from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.user_collection import UserCollection
from src.domain.repositories.user_collection_repository import UserCollectionRepository
from src.infrastructure.database.models.user_collection_model import UserCollectionModel
from src.infrastructure.database.mappers.user_collection_mapper import UserCollectionMapper

class SQLAlchemyUserCollectionRepository(UserCollectionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_user_id(self, user_id: UUID) -> Optional[UserCollection]:
        stmt = select(UserCollectionModel).where(UserCollectionModel.user_id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return UserCollectionMapper.to_domain(model) if model else None

    async def save(self, collection: UserCollection) -> None:
        # Eu busco se já existe modelo cadastrado para sincronizar itens (delete-orphan)
        stmt = select(UserCollectionModel).where(UserCollectionModel.id == collection.id)
        result = await self._session.execute(stmt)
        existing_model = result.scalar_one_or_none()

        new_model = UserCollectionMapper.to_model(collection)

        if existing_model:
            existing_model.name = new_model.name
            existing_model.items.clear()
            existing_model.items.extend(new_model.items)
        else:
            self._session.add(new_model)

        await self._session.flush()