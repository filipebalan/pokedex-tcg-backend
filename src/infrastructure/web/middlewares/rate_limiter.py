from datetime import datetime
from fastapi import Request, HTTPException, status, Depends
import redis.asyncio as aioredis
from src.infrastructure.cache.redis_client import get_redis_client

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60) -> None:
        self.requests_per_minute = requests_per_minute

    async def __call__(
        self,
        request: Request,
        redis: aioredis.Redis = Depends(get_redis_client)
    ) -> None:
        # Eu identifico a origem pelo IP do cliente (ou header de proxy X-Forwarded-For)
        client_ip = request.client.host if request.client else "unknown"
        current_minute = datetime.now().strftime("%Y%m%d%H%M")
        key = f"rate_limit:{client_ip}:{current_minute}"

        # Eu utilizo operação atômica INCR do Redis
        requests_count = await redis.incr(key)

        # Na primeira requisição da janela, eu defino a expiração em 60 segundos
        if requests_count == 1:
            await redis.expire(key, 60)

        # Se ultrapassar o limite, eu bloqueio antes de tocar no banco de dados
        if requests_count > self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Limite de requisições excedido. Tente novamente no próximo minuto.",
                headers={"Retry-After": "60"}
            )