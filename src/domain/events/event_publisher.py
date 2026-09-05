from typing import Protocol
from src.domain.events.price_changed_event import PriceChangedEvent

class EventPublisher(Protocol):
    async def publish_price_changed(self, event: PriceChangedEvent) -> None:
        """Publica assincronamente um evento de variação de preço."""
        ...