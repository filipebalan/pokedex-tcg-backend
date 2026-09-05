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
async def test_fluxo_completo_de_portfolio_autenticado() -> None:
    # 1. Eu preparo uma carta e cotação no banco
    card_id = uuid4()
    set_id = uuid4()
    async with async_session_factory() as session:
        set_repo = SQLAlchemySetRepository(session)
        card_repo = SQLAlchemyCardRepository(session)
        price_repo = SQLAlchemyPriceSnapshotRepository(session)

        await set_repo.save(Set(
            id=set_id,
            external_id=f"port_set_{uuid4().hex[:6]}",
            name="Portfolio Set",
            series="Test",
            release_date=date(2026, 1, 1),
            total_cards=10,
        ))

        await card_repo.save(Card(
            id=card_id,
            external_id=f"port_card_{uuid4().hex[:6]}",
            name="Rayquaza Gold Star",
            set_id=set_id,
            card_number="107",
            rarity="Rare Holo",
            supertype=CardSupertype.POKEMON,
        ))

        # Cotação de mercado: $350.00
        await price_repo.save(PriceSnapshot(
            card_id=card_id,
            source="tcgplayer",
            captured_at=datetime.now(timezone.utc),
            market=Money(amount=Decimal("350.00"), currency="USD"),
        ))
        await session.commit()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 2. Cadastro e Login para obter Token JWT
        user_email = f"ash_{uuid4().hex[:6]}@kanto.com"
        password = "charizard_mega_x_2026"

        await client.post("/auth/register", json={"email": user_email, "password": password})
        login_resp = await client.post("/auth/login", data={"username": user_email, "password": password})
        token = login_resp.json()["access_token"]
        auth_header = {"Authorization": f"Bearer {token}"}

        # 3. Adiciona 2 unidades da carta ao portfólio
        add_resp = await client.post(
            "/portfolio/items",
            json={"card_id": str(card_id), "quantity": 2},
            headers=auth_header
        )
        assert add_resp.status_code == 201

        # 4. Consulta o portfólio com recálculo automático de patrimônio ($350 x 2 = $700.00)
        portfolio_resp = await client.get("/portfolio", headers=auth_header)
        assert portfolio_resp.status_code == 200
        data = portfolio_resp.json()

        assert data["total_value"] == "700.00"
        assert data["total_cards_count"] == 2
        assert data["items"][0]["card_name"] == "Rayquaza Gold Star"
        assert data["items"][0]["subtotal"] == "700.00"