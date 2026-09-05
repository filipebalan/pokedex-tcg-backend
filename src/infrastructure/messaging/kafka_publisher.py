import json
import logging
from aiokafka import AIOKafkaProducer
from src.infrastructure.config.settings import settings
from src.domain.events.price_changed_event import PriceChangedEvent
from src.domain.events.event_publisher import EventPublisher

logger = logging.getLogger(__name__)

class KafkaEventPublisher(EventPublisher):
    def __init__(self, bootstrap_servers: Optional[str] = None) -> None:
        self._bootstrap_servers = bootstrap_servers or settings.KAFKA_BOOTSTRAP_SERVERS
        self._producer: Optional[AIOKafkaProducer] = None

    async def _get_producer(self) -> AIOKafkaProducer:
        if self._producer is None:
            # Eu inicializo o produtor assíncrono com serializador JSON
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self._bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8")
            )
            await self._producer.start()
        return self._producer

    async def publish_price_changed(self, event: PriceChangedEvent) -> None:
        topic = settings.KAFKA_TOPIC_PRICE_CHANGED
        payload = {
            "event_id": str(event.event_id),
            "card_id": str(event.card_id),
            "card_name": event.card_name,
            "old_price": float(event.old_price),
            "new_price": float(event.new_price),
            "percentage_change": float(event.percentage_change),
            "currency": event.currency,
            "occurred_at": event.occurred_at.isoformat()
        }

        try:
            producer = await self._get_producer()
            # Eu utilizo o card_id como chave de partição para garantir ordem dos eventos da mesma carta
            key = str(event.card_id).encode("utf-8")
            await producer.send_and_wait(topic, value=payload, key=key)
            logger.info(f"Evento de preço publicado no Kafka para {event.card_name} ({event.percentage_change:.1f}%)")
        except Exception as exc:
            # Tratamento de Falha Parcial: o log registra o erro, mas não aborta o sistema
            logger.error(f"Falha parcial ao enviar evento para o Kafka: {exc}", exc_info=True)

    async def close(self) -> None:
        if self._producer:
            await self._producer.stop()