import pytest
from httpx import AsyncClient, ASGITransport
from uuid import uuid4
from datetime import date
from src.infrastructure.web.main import app
from src.infrastructure.database.session import async_session_factory
from src.infrastructure.database.repositories.sqlalchemy_set_repository import SQLAlchemySetRepository
from src.infrastructure.database.repositories.sqlalchemy_card_repository import SQLAlchemyCardRepository
from src.domain.entities.set import Set
from src.domain.entities.card import Card
from src.domain.value_objects.card_types import CardSupertype, EnergyType

@pytest.mark.asyncio
async def test_get_cards_deve_retornar_lista_paginada_com_sucesso() -> None:
    # 1. Eu crio uma carta no banco de dados para garantir que a consulta encontre dados
    async with async_session_factory() as session:
        set_repo = SQLAlchemySetRepository(session)
        card_repo = SQLAlchemyCardRepository(session)

        set_id = uuid4()
        colecao = Set(
            id=set_id,
            external_id=f"api_test_set_{uuid4().hex[:6]}",
            name="API Test Set",
            series="Test",
            release_date=date(2026, 1, 1),
            total_cards=10,
        )
        await set_repo.save(colecao)

        carta = Card(
            id=uuid4(),
            external_id=f"api_card_{uuid4().hex[:6]}",
            name="Pikachu Web Test",
            set_id=set_id,
            card_number="25",
            rarity="Common",
            supertype=CardSupertype.POKEMON,
            types=[EnergyType.LIGHTNING],
            hp=60,
            national_dex_number=25,
        )
        await card_repo.save(carta)
        await session.commit()

    # 2. Eu executo a requisição HTTP GET /cards através do cliente assíncrono do httpx
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/cards?name=Pikachu Web Test")

        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
        assert data["items"][0]["name"] == "Pikachu Web Test"
        assert data["items"][0]["card_number"] == "25"