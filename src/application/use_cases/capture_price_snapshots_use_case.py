from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Any
from uuid import uuid4
import logging
from src.domain.entities.card import Card
from src.domain.value_objects.card_types import PriceSnapshot
from src.domain.value_objects.money import Money
from src.domain.events.price_changed_event import PriceChangedEvent
from src.domain.events.event_publisher import EventPublisher
from src.domain.repositories.price_snapshot_repository import PriceSnapshotRepository
from src.infrastructure.external_apis.pokemon_tcg_client import PokemonTcgClient

logger = logging.getLogger(__name__)

class CapturePriceSnapshotsUseCase:
    # Regra do MVP: Variação mínima de 10% para disparar alerta
    VARIATION_THRESHOLD_PERCENT = Decimal("10.0")

    def __init__(
        self,
        price_repo: PriceSnapshotRepository,
        client: PokemonTcgClient,
        event_publisher: Optional[EventPublisher] = None
    ) -> None:
        self._price_repo = price_repo
        self._client = client
        self._event_publisher = event_publisher

    async def capture_for_card(self, card: Card) -> Optional[PriceSnapshot]:
        # 1. Eu busco o snapshot mais recente anterior para calcular a variação
        previous_snapshot = await self._price_repo.find_latest_by_card_id(card.id)

        raw_card = await self._client.get_card_by_id(card.external_id)
        if not raw_card:
            return None

        tcgplayer = raw_card.get("tcgplayer", {})
        prices_block = tcgplayer.get("prices", {})
        if not prices_block:
            return None

        target_variant: dict[str, Any] = (
            prices_block.get("normal")
            or prices_block.get("holofoil")
            or prices_block.get("reverseHolofoil")
            or next(iter(prices_block.values()))
        )

        market_val = target_variant.get("market")
        if market_val is None:
            return None

        market_money = Money(amount=Decimal(str(market_val)), currency="USD")
        low_val = target_variant.get("low")
        low_money = Money(amount=Decimal(str(low_val)), currency="USD") if low_val is not None else None
        high_val = target_variant.get("high")
        high_money = Money(amount=Decimal(str(high_val)), currency="USD") if high_val is not None else None

        new_snapshot = PriceSnapshot(
            card_id=card.id,
            source="tcgplayer",
            captured_at=datetime.now(timezone.utc),
            market=market_money,
            low=low_money,
            high=high_money,
        )

        # 2. Eu gravo o novo snapshot no PostgreSQL (Fonte da Verdade)
        await self._price_repo.save(new_snapshot)

        # 3. Eu calculo a variação percentual em relação ao dia anterior
        if previous_snapshot and previous_snapshot.market.amount > Decimal("0.00"):
            old_price = previous_snapshot.market.amount
            new_price = new_snapshot.market.amount
            
            diff = new_price - old_price
            percentage_change = (diff / old_price) * Decimal("100.0")

            # Se a variação for >= 10% (subida ou queda brusca), eu disparo o evento assíncrono
            if abs(percentage_change) >= self.VARIATION_THRESHOLD_PERCENT and self._event_publisher:
                event = PriceChangedEvent(
                    event_id=uuid4(),
                    card_id=card.id,
                    card_name=card.name,
                    old_price=old_price,
                    new_price=new_price,
                    percentage_change=percentage_change.quantize(Decimal("0.1")),
                    currency=new_snapshot.market.currency,
                    occurred_at=new_snapshot.captured_at
                )
                await self._event_publisher.publish_price_changed(event)

        return new_snapshot