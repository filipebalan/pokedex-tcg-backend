import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from decimal import Decimal
from src.application.use_cases.capture_price_snapshots_use_case import CapturePriceSnapshotsUseCase
from src.domain.entities.card import Card
from src.domain.value_objects.card_types import CardSupertype

@pytest.mark.asyncio
async def test_capture_for_card_deve_extrair_preco_e_salvar_snapshot() -> None:
    # 1. Eu mocko o cliente simulando o formato oficial da pokemontcg.io v2
    mock_client = AsyncMock()
    mock_client.get_card_by_id.return_value = {
        "id": "base1-4",
        "name": "Charizard",
        "tcgplayer": {
            "prices": {
                "holofoil": {
                    "low": 150.0,
                    "market": 280.50,
                    "high": 400.0
                }
            }
        }
    }

    mock_price_repo = AsyncMock()

    use_case = CapturePriceSnapshotsUseCase(
        price_repo=mock_price_repo,
        client=mock_client
    )

    card = Card(
        id=uuid4(),
        external_id="base1-4",
        name="Charizard",
        set_id=uuid4(),
        card_number="4",
        rarity="Rare Holo",
        supertype=CardSupertype.POKEMON,
    )

    snapshot = await use_case.capture_for_card(card)

    assert snapshot is not None
    assert snapshot.market.amount == Decimal("280.50")
    assert snapshot.low is not None and snapshot.low.amount == Decimal("150.00")
    mock_price_repo.save.assert_awaited_once()