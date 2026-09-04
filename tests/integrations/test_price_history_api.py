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
async def test_get_price_history_deve_retornar_serie_temporal_da_carta() -> None:
    card_id = uuid4()
    set_id = uuid4()

    async with async_session_factory() as session:
        set_repo = SQLAlchemySetRepository(session)
        card_repo = SQLAlchemyCardRepository(session)
        price_repo = SQLAlchemyPriceSnapshotRepository(session)

        # 1. Eu crio a coleção, a carta e o snapshot no banco real
        await set_repo.save(Set(
            id=set_id,
            external_id=f"history_set_{uuid4().hex[:6]}",
            name="History Set",
            series="Test",
            release_date=date(2026, 1, 1),
            total_cards=10,
        ))

        await card_repo.save(Card(
            id=card_id,
            external_id=f"history_card_{uuid4().hex[:6]}",
            name="Mewtwo History Test",
            set_id=set_id,
            card_number="150",
            rarity="Rare Holo",
            supertype=CardSupertype.POKEMON,
        ))

        await price_repo.save(PriceSnapshot(
            card_id=card_id,
            source="tcgplayer",
            captured_at=datetime.now(timezone.utc),
            market=Money(amount=Decimal("75.00"), currency="USD"),
            low=Money(amount=Decimal("70.00"), currency="USD"),
            high=Money(amount=Decimal("85.00"), currency="USD"),
        ))
        await session.commit()

    # 2. Eu consulto a API Web
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/cards/{card_id}/price-history")

        assert response.status_code == 200
        data = response.json()

        assert data["card_id"] == str(card_id)
        assert data["total_points"] >= 1
        assert data["history"][0]["market"] == "75.00"
        assert data["history"][0]["currency"] == "USD"