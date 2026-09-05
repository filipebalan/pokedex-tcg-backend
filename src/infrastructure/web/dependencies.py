from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis
from src.infrastructure.database.session import get_db_session
from src.infrastructure.cache.redis_client import get_redis_client
from src.infrastructure.cache.price_history_cache import PriceHistoryCacheService
from src.infrastructure.security.token_service import TokenService
from src.infrastructure.database.repositories.sqlalchemy_card_repository import SQLAlchemyCardRepository
from src.infrastructure.database.repositories.sqlalchemy_price_snapshot_repository import SQLAlchemyPriceSnapshotRepository
from src.infrastructure.database.repositories.sqlalchemy_user_repository import SQLAlchemyUserRepository
from src.infrastructure.database.repositories.sqlalchemy_user_collection_repository import SQLAlchemyUserCollectionRepository
from src.domain.entities.user import User
from src.domain.repositories.card_repository import CardRepository
from src.domain.repositories.price_snapshot_repository import PriceSnapshotRepository
from src.domain.repositories.user_repository import UserRepository
from src.domain.repositories.user_collection_repository import UserCollectionRepository

# Esquema oficial OAuth2 Bearer apontando para o endpoint de login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
token_service = TokenService()

def get_card_repository(session: AsyncSession = Depends(get_db_session)) -> CardRepository:
    return SQLAlchemyCardRepository(session)

def get_price_snapshot_repository(session: AsyncSession = Depends(get_db_session)) -> PriceSnapshotRepository:
    return SQLAlchemyPriceSnapshotRepository(session)

def get_user_repository(session: AsyncSession = Depends(get_db_session)) -> UserRepository:
    return SQLAlchemyUserRepository(session)

def get_user_collection_repository(session: AsyncSession = Depends(get_db_session)) -> UserCollectionRepository:
    return SQLAlchemyUserCollectionRepository(session)

def get_price_history_cache_service(redis: aioredis.Redis = Depends(get_redis_client)) -> PriceHistoryCacheService:
    return PriceHistoryCacheService(redis)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repo: UserRepository = Depends(get_user_repository)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = token_service.decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    user = await user_repo.find_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user