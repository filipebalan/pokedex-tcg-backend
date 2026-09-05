import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from datetime import datetime, timezone, date
from decimal import Decimal
from src.infrastructure.web.main import app
from src.infrastructure.database.session import async_session_factory
from src.infrastructure.database.repositories.sqlalchemy_set_repository import SQLAlchemySetRepository
from src.infrastructure.database.repositories.sqlalchemy_card_repository import SQLAlchemyCardRepository
from src.infrastructure.database.repositories.sqlalchemy_price_snapshot_repository import SQLAlchemyPriceSnapshotRepository
from src.domain.entities.set import Set
from src.domain.entities.card import Card
from src.domain.value_objects.card_types import CardSupertype, PriceSnapshot
from src.domain.value_objects.money import Money

@pytest.mark.asyncio
async def test_post_collection_value_deve_retornar_soma_correta_via_api() -> None:
    card_id = uuid4()
    set_id = uuid4()

    async with async_session_factory() as session:
        set_repo = SQLAlchemySetRepository(session)
        card_repo = SQLAlchemyCardRepository(session)
        price_repo = SQLAlchemyPriceSnapshotRepository(session)

        await set_repo.save(Set(
            id=set_id,
            external_id=f"calc_set_{uuid4().hex[:6]}",
            name="Calc Set",
            series="Test",
            release_date=date(2026, 1, 1),
            total_cards=10,
        ))

        await card_repo.save(Card(
            id=card_id,
            external_id=f"calc_card_{uuid4().hex[:6]}",
            name="Mewtwo Collection Test",
            set_id=set_id,
            card_number="10",
            rarity="Rare Holo",
            supertype=CardSupertype.POKEMON,
        ))

        # Cotação: $50.00
        await price_repo.save(PriceSnapshot(
            card_id=card_id,
            source="tcgplayer",
            captured_at=datetime.now(timezone.utc),
            market=Money(amount=Decimal("50.00"), currency="USD"),
        ))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Eu envio quantidade 4 de Mewtwo ($50 x 4 = $200.00)
        payload = {
            "items": [
                {"card_id": str(card_id), "quantity": 4}
            ]
        }
        response = await client.post("/collection/value", json=payload)

        assert response.status_code == 200
        data = response.json()

        assert data["total_value"] == "200.00"
        assert data["currency"] == "USD"
        assert data["total_cards_count"] == 4
        assert data["priced_items_count"] == 1
        assert data["items"][0]["subtotal"] == "200.00"