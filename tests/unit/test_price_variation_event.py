import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, timezone
from decimal import Decimal
from src.application.use_cases.capture_price_snapshots_use_case import CapturePriceSnapshotsUseCase
from src.domain.entities.card import Card
from src.domain.value_objects.card_types import CardSupertype, PriceSnapshot
from src.domain.value_objects.money import Money

@pytest.mark.asyncio
async def test_deve_disparar_evento_quando_variacao_for_maior_ou_igual_a_dez_porcento() -> None:
    card_id = uuid4()
    mock_price_repo = AsyncMock()
    # Cotação anterior: $100.00
    mock_price_repo.find_latest_by_card_id.return_value = PriceSnapshot(
        card_id=card_id,
        source="tcgplayer",
        captured_at=datetime.now(timezone.utc),
        market=Money(amount=Decimal("100.00"), currency="USD")
    )

    mock_client = AsyncMock()
    # Nova cotação: $115.00 (+15% de variação)
    mock_client.get_card_by_id.return_value = {
        "id": "base1-4",
        "name": "Charizard",
        "tcgplayer": {"prices": {"holofoil": {"market": 115.00}}}
    }

    mock_publisher = AsyncMock()

    use_case = CapturePriceSnapshotsUseCase(
        price_repo=mock_price_repo,
        client=mock_client,
        event_publisher=mock_publisher
    )

    card = Card(
        id=card_id,
        external_id="base1-4",
        name="Charizard",
        set_id=uuid4(),
        card_number="4",
        rarity="Rare Holo",
        supertype=CardSupertype.POKEMON,
    )

    await use_case.capture_for_card(card)

    # Eu garanto que o evento foi publicado no Kafka
    mock_publisher.publish_price_changed.assert_awaited_once()

@pytest.mark.asyncio
async def test_nao_deve_disparar_evento_quando_variacao_for_menor_que_dez_porcento() -> None:
    card_id = uuid4()
    mock_price_repo = AsyncMock()
    # Cotação anterior: $100.00
    mock_price_repo.find_latest_by_card_id.return_value = PriceSnapshot(
        card_id=card_id,
        source="tcgplayer",
        captured_at=datetime.now(timezone.utc),
        market=Money(amount=Decimal("100.00"), currency="USD")
    )

    mock_client = AsyncMock()
    # Nova cotação: $105.00 (+5% de variação, abaixo do limite de 10%)
    mock_client.get_card_by_id.return_value = {
        "id": "base1-4",
        "name": "Charizard",
        "tcgplayer": {"prices": {"holofoil": {"market": 105.00}}}
    }

    mock_publisher = AsyncMock()

    use_case = CapturePriceSnapshotsUseCase(
        price_repo=mock_price_repo,
        client=mock_client,
        event_publisher=mock_publisher
    )

    card = Card(
        id=card_id,
        external_id="base1-4",
        name="Charizard",
        set_id=uuid4(),
        card_number="4",
        rarity="Rare Holo",
        supertype=CardSupertype.POKEMON,
    )

    await use_case.capture_for_card(card)

    # Eu garanto que o evento NÃO foi publicado
    mock_publisher.publish_price_changed.assert_not_awaited()