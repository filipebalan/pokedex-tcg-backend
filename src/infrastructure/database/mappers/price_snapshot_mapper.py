from decimal import Decimal
from src.domain.value_objects.card_types import PriceSnapshot
from src.domain.value_objects.money import Money
from src.infrastructure.database.models.price_snapshot_model import PriceSnapshotModel

class PriceSnapshotMapper:
    @staticmethod
    def to_domain(model: PriceSnapshotModel) -> PriceSnapshot:
        # Eu reconstruo os Value Objects Money a partir dos decimais do banco
        market_money = Money(amount=model.price_market, currency=model.currency)
        low_money = Money(amount=model.price_low, currency=model.currency) if model.price_low is not None else None
        high_money = Money(amount=model.price_high, currency=model.currency) if model.price_high is not None else None

        return PriceSnapshot(
            card_id=model.card_id,
            source=model.source,
            captured_at=model.captured_at,
            market=market_money,
            low=low_money,
            high=high_money,
        )

    @staticmethod
    def to_model(entity: PriceSnapshot) -> PriceSnapshotModel:
        # Eu extraio os primitivos numéricos do Value Object para as colunas do PostgreSQL
        return PriceSnapshotModel(
            card_id=entity.card_id,
            source=entity.source,
            captured_at=entity.captured_at,
            currency=entity.market.currency,
            price_market=entity.market.amount,
            price_low=entity.low.amount if entity.low else None,
            price_high=entity.high.amount if entity.high else None,
        )