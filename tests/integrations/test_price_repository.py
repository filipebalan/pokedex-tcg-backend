import pytest
from uuid import uuid4
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal
import src.infrastructure.database.models
from src.infrastructure.database.session import async_session_factory
from src.infrastructure.database.repositories.sqlalchemy_set_repository import SQLAlchemySetRepository
from src.infrastructure.database.repositories.sqlalchemy_card_repository import SQLAlchemyCardRepository
from src.infrastructure.database.repositories.sqlalchemy_price_snapshot_repository import SQLAlchemyPriceSnapshotRepository
from src.domain.entities.set import Set
from src.domain.entities.card import Card
from src.domain.value_objects.card_types import CardSupertype, PriceSnapshot
from src.domain.value_objects.money import Money

@pytest.mark.asyncio
async def test_deve_persistir_snapshots_e_recuperar_serie_temporal_ordenada() -> None:
    async with async_session_factory() as session:
        set_repo = SQLAlchemySetRepository(session)
        card_repo = SQLAlchemyCardRepository(session)
        price_repo = SQLAlchemyPriceSnapshotRepository(session)

        # 1. Eu crio uma coleção e uma carta base
        set_id = uuid4()
        colecao = Set(
            id=set_id,
            external_id=f"set_price_{uuid4().hex[:6]}",
            name="Price Test Set",
            series="Test",
            release_date=date(2026, 1, 1),
            total_cards=10,
        )
        await set_repo.save(colecao)

        card_id = uuid4()
        carta = Card(
            id=card_id,
            external_id=f"card_price_{uuid4().hex[:6]}",
            name="Gengar Holo",
            set_id=set_id,
            card_number="94",
            rarity="Rare Holo",
            supertype=CardSupertype.POKEMON,
        )
        await card_repo.save(carta)

        # 2. Eu registro cotações em dois dias consecutivos
        agora = datetime.now(timezone.utc)
        ontem = agora - timedelta(days=1)

        snapshot_ontem = PriceSnapshot(
            card_id=card_id,
            source="tcgplayer",
            captured_at=ontem,
            market=Money(amount=Decimal("100.00"), currency="USD"),
            low=Money(amount=Decimal("90.00"), currency="USD"),
            high=Money(amount=Decimal("110.00"), currency="USD"),
        )

        snapshot_hoje = PriceSnapshot(
            card_id=card_id,
            source="tcgplayer",
            captured_at=agora,
            market=Money(amount=Decimal("125.00"), currency="USD"),  # Subiu de preço
            low=Money(amount=Decimal("115.00"), currency="USD"),
            high=Money(amount=Decimal("140.00"), currency="USD"),
        )

        await price_repo.save(snapshot_ontem)
        await price_repo.save(snapshot_hoje)
        await session.commit()

       # 3. Eu busco o histórico da carta
        historico = await price_repo.list_by_card_id(card_id)

        assert len(historico) == 2
        # Eu valido a ordem cronológica
        assert historico[0].market.amount == Decimal("100.00")
        assert historico[1].market.amount == Decimal("125.00")
        assert historico[0].captured_at < historico[1].captured_at