from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

@dataclass(frozen=True, slots=True)
class PriceChangedEvent:
    # Eu defino o evento como imutável com ID único para garantir idempotência no consumidor
    event_id: UUID
    card_id: UUID
    card_name: str
    old_price: Decimal
    new_price: Decimal
    percentage_change: Decimal
    currency: str
    occurred_at: datetime