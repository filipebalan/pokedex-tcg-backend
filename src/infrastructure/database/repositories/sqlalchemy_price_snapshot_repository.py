from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.value_objects.card_types import PriceSnapshot
from src.domain.repositories.price_snapshot_repository import PriceSnapshotRepository
from src.infrastructure.database.models.price_snapshot_model import PriceSnapshotModel
from src.infrastructure.database.mappers.price_snapshot_mapper import PriceSnapshotMapper

class SQLAlchemyPriceSnapshotRepository(PriceSnapshotRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, snapshot: PriceSnapshot) -> None:
        # Eu crio o registro imutável no banco de dados (append-only)
        model = PriceSnapshotMapper.to_model(snapshot)
        self._session.add(model)
        await self._session.flush()

    async def list_by_card_id(
        self,
        card_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[PriceSnapshot]:
        # Eu monto a consulta da série temporal filtrada por carta e intervalo de datas
        stmt = select(PriceSnapshotModel).where(PriceSnapshotModel.card_id == card_id)

        if start_date:
            stmt = stmt.where(PriceSnapshotModel.captured_at >= start_date)
        if end_date:
            stmt = stmt.where(PriceSnapshotModel.captured_at <= end_date)

        # Eu ordeno cronologicamente para consumo do gráfico
        stmt = stmt.order_by(PriceSnapshotModel.captured_at.asc())
        result = await self._session.execute(stmt)
        models = result.scalars().all()

        return [PriceSnapshotMapper.to_domain(m) for m in models]

    async def find_latest_by_card_id(self, card_id: UUID) -> Optional[PriceSnapshot]:
        # Eu busco apenas o último snapshot ordenado por data descendente (LIMIT 1)
        stmt = (
            select(PriceSnapshotModel)
            .where(PriceSnapshotModel.card_id == card_id)
            .order_by(PriceSnapshotModel.captured_at.desc())
            .limit(1)
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return PriceSnapshotMapper.to_domain(model) if model else None