from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class PricePointDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    captured_at: datetime
    source: str
    currency: str
    market: Decimal
    low: Optional[Decimal] = None
    high: Optional[Decimal] = None

class CardPriceHistoryResponseDTO(BaseModel):
    card_id: UUID
    total_points: int
    history: list[PricePointDTO]