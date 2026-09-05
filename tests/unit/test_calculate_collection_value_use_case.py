import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal
from src.application.use_cases.calculate_collection_value_use_case import CalculateCollectionValueUseCase
from src.domain.entities.card import Card
from src.domain.value_objects.card_types import CardSupertype, PriceSnapshot
from src.domain.value_objects.money import Money

@pytest.mark.asyncio
async def test_deve_calcular_valor_total_da_colecao_com_multiplicacao_correta() -> None:
    card1_id = uuid4()
    card2_id = uuid4()

    mock_card_repo = AsyncMock()
    mock_card_repo.find_by_id.side_effect = lambda cid: Card(
        id=cid,
        external_id="test",
        name="Charizard" if cid == card1_id else "Pikachu",
        set_id=uuid4(),
        card_number="1",
        rarity="Rare",
        supertype=CardSupertype.POKEMON
    )

    mock_price_repo = AsyncMock()
    # Charizard: $100.00 | Pikachu: $10.00
    mock_price_repo.find_latest_by_card_id.side_effect = lambda cid: PriceSnapshot(
        card_id=cid,
        source="tcgplayer",
        captured_at=datetime.now(timezone.utc),
        market=Money(amount=Decimal("100.00") if cid == card1_id else Decimal("10.00"), currency="USD")
    )

    use_case = CalculateCollectionValueUseCase(
        card_repo=mock_card_repo,
        price_repo=mock_price_repo
    )

    # Eu envio 2 Charizards ($200) e 3 Pikachus ($30)
    items = [(card1_id, 2), (card2_id, 3)]
    resultado = await use_case.calculate(items)

    # Total esperado: $230.00 em 5 cartas
    assert resultado.total_value.amount == Decimal("230.00")
    assert resultado.total_cards_count == 5
    assert resultado.priced_items_count == 2
    assert resultado.unpriced_items_count == 0