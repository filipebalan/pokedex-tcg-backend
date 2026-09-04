from uuid import uuid4
from datetime import datetime
from decimal import Decimal
import pytest
from src.domain.value_objects.card_types import PriceSnapshot
from src.domain.value_objects.money import Money

def test_price_snapshot_deve_ser_criado_com_sucesso_quando_precos_forem_consistentes() -> None:
    # Eu crio uma cotação com valores válidos em dólar
    snapshot = PriceSnapshot(
        card_id=uuid4(),
        source="tcgplayer",
        captured_at=datetime.now(),
        low=Money(amount=Decimal("10.00"), currency="USD"),
        market=Money(amount=Decimal("15.50"), currency="USD"),
        high=Money(amount=Decimal("20.00"), currency="USD"),
    )

    assert snapshot.source == "tcgplayer"
    assert snapshot.market.amount == Decimal("15.50")
    assert snapshot.low is not None and snapshot.low.amount == Decimal("10.00")

def test_price_snapshot_deve_permitir_criacao_sem_limites_low_e_high() -> None:
    # Eu valido que uma carta que possui apenas preço de mercado é aceita pelo domínio
    snapshot = PriceSnapshot(
        card_id=uuid4(),
        source="tcgplayer",
        captured_at=datetime.now(),
        market=Money(amount=Decimal("50.00"), currency="USD")
    )

    assert snapshot.market.amount == Decimal("50.00")
    assert snapshot.low is None
    assert snapshot.high is None

def test_price_snapshot_deve_falhar_quando_moedas_forem_diferentes() -> None:
    # Eu forço erro ao misturar moedas em um mesmo registro
    with pytest.raises(ValueError, match="difere da moeda de mercado"):
        PriceSnapshot(
            card_id=uuid4(),
            source="tcgplayer",
            captured_at=datetime.now(),
            low=Money(amount=Decimal("10.00"), currency="BRL"),
            market=Money(amount=Decimal("15.50"), currency="USD"),
        )

def test_price_snapshot_deve_falhar_quando_low_for_maior_que_market() -> None:
    # Eu valido que o domínio rejeita cotação impossível
    with pytest.raises(ValueError, match="Inconsistência de mercado"):
        PriceSnapshot(
            card_id=uuid4(),
            source="tcgplayer",
            captured_at=datetime.now(),
            low=Money(amount=Decimal("25.00"), currency="USD"),  # low maior que market
            market=Money(amount=Decimal("15.00"), currency="USD")
        )