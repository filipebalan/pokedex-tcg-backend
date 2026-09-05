import json
import logging
from typing import Optional
from aiokafka import AIOKafkaConsumer
import redis.asyncio as aioredis
from src.infrastructure.config.settings import settings

logger = logging.getLogger(__name__)

class PriceAlertConsumer:
    def __init__(
        self,
        redis: aioredis.Redis,
        bootstrap_servers: Optional[str] = None
    ) -> None:
        self._redis = redis
        self._bootstrap_servers = bootstrap_servers or settings.KAFKA_BOOTSTRAP_SERVERS
        self._consumer: Optional[AIOKafkaConsumer] = None

    async def start(self) -> None:
        # Eu inicio o consumidor assíncrono escutando o tópico de alertas
        self._consumer = AIOKafkaConsumer(
            settings.KAFKA_TOPIC_PRICE_CHANGED,
            bootstrap_servers=self._bootstrap_servers,
            group_id="pokedex_alert_group",
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest"
        )
        await self._consumer.start()
        logger.info("Consumidor do Kafka iniciado e ouvindo o tópico 'price-changed'.")

    async def consume_one(self) -> Optional[dict]:
        # Método utilitário para testes ou loop do worker
        if not self._consumer:
            return None

        msg = await self._consumer.getone()
        event_data = msg.value
        event_id = event_data["event_id"]

        # Eu utilizo o Redis para garantir Idempotência estrita (chave expira em 24h)
        idempotency_key = f"idempotency:event:{event_id}"
        is_new = await self._redis.set(idempotency_key, "processed", nx=True, ex=86400)

        if not is_new:
            logger.warning(f"Mensagem duplicada ignorada pelo consumidor: {event_id}")
            return None

        # Processamento do alerta (simulação de envio de email ou push)
        logger.info(
            f"🔔 [ALERTA DE PREÇO] Carta: {event_data['card_name']} | "
            f"Preço Anterior: {event_data['currency']} {event_data['old_price']:.2f} ➔ "
            f"Novo Preço: {event_data['currency']} {event_data['new_price']:.2f} | "
            f"Variação: {event_data['percentage_change']:+.1f}%"
        )
        return event_data

    async def stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()