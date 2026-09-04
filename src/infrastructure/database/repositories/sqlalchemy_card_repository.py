from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.entities.card import Card
from src.domain.repositories.card_repository import CardRepository
from src.infrastructure.database.models.card_model import CardModel
from src.infrastructure.database.mappers.card_mapper import CardMapper

class SQLAlchemyCardRepository(CardRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_id(self, card_id: UUID) -> Optional[Card]:
        stmt = select(CardModel).where(CardModel.id == card_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return CardMapper.to_domain(model) if model else None

    async def find_by_external_id(self, external_id: str) -> Optional[Card]:
        stmt = select(CardModel).where(CardModel.external_id == external_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return CardMapper.to_domain(model) if model else None

    async def list_cards(
        self,
        set_id: Optional[UUID] = None,
        name: Optional[str] = None,
        rarity: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Card]:
        # Eu monto a query dinâmica com filtros opcionais e paginação
        stmt = select(CardModel)

        if set_id:
            stmt = stmt.where(CardModel.set_id == set_id)
        if name:
            stmt = stmt.where(CardModel.name.ilike(f"%{name}%"))
        if rarity:
            stmt = stmt.where(CardModel.rarity == rarity)

        stmt = stmt.order_by(CardModel.card_number).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        return [CardMapper.to_domain(m) for m in models]

    async def save(self, card: Card) -> None:
        # Upsert idempotente de carta
        raw_types = [t.value for t in card.types]

        stmt = insert(CardModel).values(
            id=card.id,
            external_id=card.external_id,
            name=card.name,
            set_id=card.set_id,
            card_number=card.card_number,
            rarity=card.rarity,
            supertype=card.supertype.value,
            types=raw_types,
            hp=card.hp,
            national_dex_number=card.national_dex_number,
        )

        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=[CardModel.external_id],
            set_={
                "name": stmt.excluded.name,
                "card_number": stmt.excluded.card_number,
                "rarity": stmt.excluded.rarity,
                "supertype": stmt.excluded.supertype,
                "types": stmt.excluded.types,
                "hp": stmt.excluded.hp,
                "national_dex_number": stmt.excluded.national_dex_number,
            }
        )

        await self._session.execute(upsert_stmt)