import pytest
from uuid import uuid4
from datetime import date
# Eu importo os models para garantir que o SQLAlchemy inicialize todo o registro de relacionamentos
import src.infrastructure.database.models
from src.infrastructure.database.session import async_session_factory
from src.infrastructure.database.repositories.sqlalchemy_set_repository import SQLAlchemySetRepository
from src.infrastructure.database.repositories.sqlalchemy_card_repository import SQLAlchemyCardRepository
from src.domain.entities.set import Set
from src.domain.entities.card import Card
from src.domain.value_objects.card_types import CardSupertype, EnergyType

@pytest.mark.asyncio
async def test_deve_persistir_e_recuperar_set_e_card_no_banco_real() -> None:
    async with async_session_factory() as session:
        set_repo = SQLAlchemySetRepository(session)
        card_repo = SQLAlchemyCardRepository(session)

        # 1. Eu crio e persisto uma coleção
        set_id = uuid4()
        base_set = Set(
            id=set_id,
            external_id=f"base_test_{uuid4().hex[:6]}",
            name="Base Set Integration",
            series="Base",
            release_date=date(1999, 1, 9),
            total_cards=102,
        )
        await set_repo.save(base_set)

        # 2. Eu crio e persisto uma carta associada a essa coleção
        card_id = uuid4()
        charizard = Card(
            id=card_id,
            external_id=f"charizard_test_{uuid4().hex[:6]}",
            name="Charizard",
            set_id=set_id,
            card_number="4",
            rarity="Rare Holo",
            supertype=CardSupertype.POKEMON,
            types=[EnergyType.FIRE],
            hp=120,
            national_dex_number=6,
        )
        await card_repo.save(charizard)

        # Eu comito a transação no PostgreSQL
        await session.commit()

        # 3. Eu busco a carta do banco pelo external_id
        carta_encontrada = await card_repo.find_by_external_id(charizard.external_id)

        assert carta_encontrada is not None
        assert carta_encontrada.id == card_id
        assert carta_encontrada.name == "Charizard"
        assert carta_encontrada.hp == 120
        assert carta_encontrada.types == [EnergyType.FIRE]