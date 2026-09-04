from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.set import Set
from src.domain.repositories.set_repository import SetRepository
from src.infrastructure.database.models.set_model import SetModel
from src.infrastructure.database.mappers.set_mapper import SetMapper

class SQLAlchemySetRepository(SetRepository):
    def __init__(self, session: AsyncSession) -> None:
        # Eu recebo a sessão assíncrona do banco via Injeção de Dependência
        self._session = session

    async def find_by_id(self, set_id: UUID) -> Optional[Set]:
        stmt = select(SetModel).where(SetModel.id == set_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return SetMapper.to_domain(model) if model else None

    async def find_by_external_id(self, external_id: str) -> Optional[Set]:
        stmt = select(SetModel).where(SetModel.external_id == external_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return SetMapper.to_domain(model) if model else None

    async def save(self, collection_set: Set) -> None:
        # Eu implemento Upsert atômico e idempotente utilizando a cláusula ON CONFLICT do PostgreSQL
        stmt = insert(SetModel).values(
            id=collection_set.id,
            external_id=collection_set.external_id,
            name=collection_set.name,
            series=collection_set.series,
            release_date=collection_set.release_date,
            total_cards=collection_set.total_cards,
        )

        # Se já existir uma coleção com o mesmo external_id, eu atualizo os dados mutáveis
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[SetModel.external_id],
            set_={
                "name": stmt.excluded.name,
                "series": stmt.excluded.series,
                "release_date": stmt.excluded.release_date,
                "total_cards": stmt.excluded.total_cards,
            }
        )

        await self._session.execute(upsert_stmt)