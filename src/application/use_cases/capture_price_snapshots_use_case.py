from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Any
from src.domain.entities.card import Card
from src.domain.value_objects.card_types import PriceSnapshot
from src.domain.value_objects.money import Money
from src.domain.repositories.price_snapshot_repository import PriceSnapshotRepository
from src.infrastructure.external_apis.pokemon_tcg_client import PokemonTcgClient

class CapturePriceSnapshotsUseCase:
    def __init__(
        self,
        price_repo: PriceSnapshotRepository,
        client: PokemonTcgClient
    ) -> None:
        self._price_repo = price_repo
        self._client = client

    async def capture_for_card(self, card: Card) -> Optional[PriceSnapshot]:
        # 1. Eu busco os dados em tempo real da carta na API externa
        raw_card = await self._client.get_card_by_id(card.external_id)
        if not raw_card:
            return None

        tcgplayer = raw_card.get("tcgplayer", {})
        prices_block = tcgplayer.get("prices", {})
        if not prices_block:
            return None

        # 2. Eu seleciono a cotação válida (priorizando normal, holofoil ou o primeiro acabamento disponível)
        target_variant: dict[str, Any] = (
            prices_block.get("normal")
            or prices_block.get("holofoil")
            or prices_block.get("reverseHolofoil")
            or next(iter(prices_block.values()))
        )

        market_val = target_variant.get("market")
        if market_val is None:
            return None

        # 3. Eu construo os Value Objects Money com precisão decimal
        market_money = Money(amount=Decimal(str(market_val)), currency="USD")
        
        low_val = target_variant.get("low")
        low_money = Money(amount=Decimal(str(low_val)), currency="USD") if low_val is not None else None

        high_val = target_variant.get("high")
        high_money = Money(amount=Decimal(str(high_val)), currency="USD") if high_val is not None else None

        # 4. Eu monto o registro imutável do snapshot
        snapshot = PriceSnapshot(
            card_id=card.id,
            source="tcgplayer",
            captured_at=datetime.now(timezone.utc),
            market=market_money,
            low=low_money,
            high=high_money,
        )

        # 5. Eu salvo de forma append-only no repositório
        await self._price_repo.save(snapshot)
        return snapshot