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
async def test_get_price_history_deve_utilizar_cache_redis_com_hit_e_miss() -> None:
    card_id = uuid4()
    set_id = uuid4()

    # 1. Eu crio os dados iniciais no banco
    async with async_session_factory() as session:
        set_repo = SQLAlchemySetRepository(session)
        card_repo = SQLAlchemyCardRepository(session)
        price_repo = SQLAlchemyPriceSnapshotRepository(session)

        await set_repo.save(Set(
            id=set_id,
            external_id=f"cache_set_{uuid4().hex[:6]}",
            name="Cache Set",
            series="Test",
            release_date=date(2026, 1, 1),
            total_cards=10,
        ))

        await card_repo.save(Card(
            id=card_id,
            external_id=f"cache_card_{uuid4().hex[:6]}",
            name="Alakazam Cache Test",
            set_id=set_id,
            card_number="65",
            rarity="Rare",
            supertype=CardSupertype.POKEMON,
        ))

        await price_repo.save(PriceSnapshot(
            card_id=card_id,
            source="tcgplayer",
            captured_at=datetime.now(timezone.utc),
            market=Money(amount=Decimal("40.00"), currency="USD"),
        ))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 2. Primeira requisição: Deve ir ao banco (Cache MISS)
        resp1 = await client.get(f"/cards/{card_id}/price-history")
        assert resp1.status_code == 200
        assert resp1.headers.get("X-Cache") == "MISS"
        data1 = resp1.json()
        assert data1["total_points"] == 1

        # 3. Segunda requisição idêntica: Deve vir da memória do Redis (Cache HIT)
        resp2 = await client.get(f"/cards/{card_id}/price-history")
        assert resp2.status_code == 200
        assert resp2.headers.get("X-Cache") == "HIT"
        data2 = resp2.json()
        assert data2 == data1