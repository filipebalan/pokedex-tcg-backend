from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.database.session import get_db_session
from src.infrastructure.database.repositories.sqlalchemy_card_repository import SQLAlchemyCardRepository
from src.domain.repositories.card_repository import CardRepository
from src.infrastructure.database.repositories.sqlalchemy_price_snapshot_repository import SQLAlchemyPriceSnapshotRepository
from src.domain.repositories.price_snapshot_repository import PriceSnapshotRepository

def get_price_snapshot_repository(
    session: AsyncSession = Depends(get_db_session)
) -> PriceSnapshotRepository:
    return SQLAlchemyPriceSnapshotRepository(session)

def get_card_repository(
    session: AsyncSession = Depends(get_db_session)
) -> CardRepository:
    # Eu instancio a implementação concreta do repositório vinculada à sessão da requisição
    return SQLAlchemyCardRepository(session)