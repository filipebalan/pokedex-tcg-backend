from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis
from src.infrastructure.database.session import get_db_session
from src.infrastructure.cache.redis_client import get_redis_client
from src.infrastructure.cache.price_history_cache import PriceHistoryCacheService
from src.infrastructure.database.repositories.sqlalchemy_card_repository import SQLAlchemyCardRepository
from src.infrastructure.database.repositories.sqlalchemy_price_snapshot_repository import SQLAlchemyPriceSnapshotRepository
from src.domain.repositories.card_repository import CardRepository
from src.domain.repositories.price_snapshot_repository import PriceSnapshotRepository

def get_card_repository(
    session: AsyncSession = Depends(get_db_session)
) -> CardRepository:
    return SQLAlchemyCardRepository(session)

def get_price_snapshot_repository(
    session: AsyncSession = Depends(get_db_session)
) -> PriceSnapshotRepository:
    return SQLAlchemyPriceSnapshotRepository(session)

def get_price_history_cache_service(
    redis: aioredis.Redis = Depends(get_redis_client)
) -> PriceHistoryCacheService:
    # Eu injeto o serviço de cache desacoplado
    return PriceHistoryCacheService(redis)