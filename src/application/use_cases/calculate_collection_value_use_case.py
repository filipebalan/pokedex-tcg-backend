from decimal import Decimal
from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime
from src.domain.value_objects.money import Money
from src.domain.repositories.card_repository import CardRepository
from src.domain.repositories.price_snapshot_repository import PriceSnapshotRepository

@dataclass(frozen=True, slots=True)
class ItemValuation:
    card_id: UUID
    card_name: str
    quantity: int
    unit_price: Optional[Money]
    subtotal: Optional[Money]
    price_date: Optional[datetime]

@dataclass(frozen=True, slots=True)
class CollectionValuationResult:
    total_value: Money
    total_cards_count: int
    priced_items_count: int
    unpriced_items_count: int
    items: list[ItemValuation]

class CalculateCollectionValueUseCase:
    def __init__(
        self,
        card_repo: CardRepository,
        price_repo: PriceSnapshotRepository
    ) -> None:
        self._card_repo = card_repo
        self._price_repo = price_repo

    async def calculate(self, items_to_calculate: list[tuple[UUID, int]]) -> CollectionValuationResult:
        # Eu inicio o acumulador financeiro em zero dólar
        total_money = Money(amount=Decimal("0.00"), currency="USD")
        valuation_items: list[ItemValuation] = []
        total_cards_count = 0
        priced_count = 0
        unpriced_count = 0

        for card_id, quantity in items_to_calculate:
            total_cards_count += quantity
            card = await self._card_repo.find_by_id(card_id)
            card_name = card.name if card else "Carta Desconhecida"

            # Eu busco a cotação mais recente dessa carta
            latest_snapshot = await self._price_repo.find_latest_by_card_id(card_id)

            if latest_snapshot and latest_snapshot.market.amount > Decimal("0.00"):
                unit_price = latest_snapshot.market
                # Eu utilizo o método de multiplicação do próprio Value Object Money
                subtotal = unit_price.multiply(Decimal(quantity))
                # Eu acumulo a soma total
                total_money = total_money.add(subtotal)
                priced_count += 1

                valuation_items.append(
                    ItemValuation(
                        card_id=card_id,
                        card_name=card_name,
                        quantity=quantity,
                        unit_price=unit_price,
                        subtotal=subtotal,
                        price_date=latest_snapshot.captured_at
                    )
                )
            else:
                # Tratamento de defesa: carta sem cotação recente
                unpriced_count += 1
                valuation_items.append(
                    ItemValuation(
                        card_id=card_id,
                        card_name=card_name,
                        quantity=quantity,
                        unit_price=None,
                        subtotal=None,
                        price_date=None
                    )
                )

        return CollectionValuationResult(
            total_value=total_money,
            total_cards_count=total_cards_count,
            priced_items_count=priced_count,
            unpriced_items_count=unpriced_count,
            items=valuation_items
        )