from typing import AsyncGenerator
import redis.asyncio as aioredis
from src.infrastructure.config.settings import settings

# Eu crio o pool de conexões assíncronas com o Redis do Docker
redis_pool = aioredis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    max_connections=20
)

async def get_redis_client() -> AsyncGenerator[aioredis.Redis, None]:
    # Eu utilizo um generator para gerenciar o ciclo de vida da conexão injetada
    client = aioredis.Redis(connection_pool=redis_pool)
    try:
        yield client
    finally:
        await client.aclose()