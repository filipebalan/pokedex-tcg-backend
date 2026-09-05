import json
import logging
from typing import Optional
from uuid import UUID
from datetime import datetime
import redis.asyncio as aioredis
from src.infrastructure.web.dtos.price_dtos import CardPriceHistoryResponseDTO

logger = logging.getLogger(__name__)

class PriceHistoryCacheService:
    # TTL de 1 hora (3600 segundos), pois os preços mudam apenas uma vez por dia
    DEFAULT_TTL_SECONDS = 3600

    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis

    def _build_key(self, card_id: UUID, start_date: Optional[datetime], end_date: Optional[datetime]) -> str:
        # Eu normalizo os filtros na chave para evitar colisões entre consultas com intervalos diferentes
        start_str = start_date.isoformat() if start_date else "none"
        end_str = end_date.isoformat() if end_date else "none"
        return f"cache:price_history:{card_id}:{start_str}:{end_str}"

    async def get(
        self,
        card_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[CardPriceHistoryResponseDTO]:
        key = self._build_key(card_id, start_date, end_date)
        try:
            cached_json = await self._redis.get(key)
            if cached_json:
                # Eu desserializo o JSON diretamente para o DTO do Pydantic v2
                data = json.loads(cached_json)
                return CardPriceHistoryResponseDTO.model_validate(data)
        except Exception as exc:
            # Estratégia Fail-Open: eu logo o erro sem propagar exceção para o usuário
            logger.warning(f"Falha ao consultar cache no Redis para chave {key}: {exc}")
        
        return None

    async def set(
        self,
        card_id: UUID,
        dto: CardPriceHistoryResponseDTO,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> None:
        key = self._build_key(card_id, start_date, end_date)
        try:
            # Eu serializo o DTO do Pydantic v2 em JSON seguro
            payload = dto.model_dump_json()
            await self._redis.set(key, payload, ex=self.DEFAULT_TTL_SECONDS)
        except Exception as exc:
            logger.warning(f"Falha ao gravar cache no Redis para chave {key}: {exc}")