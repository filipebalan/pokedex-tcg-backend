from uuid import UUID
from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

class CollectionItemInputDTO(BaseModel):
    card_id: UUID
    quantity: int = Field(gt=0, description="Quantidade da carta (deve ser maior que zero)")

class CalculateCollectionRequestDTO(BaseModel):
    items: list[CollectionItemInputDTO] = Field(min_length=1, description="Lista de cartas da coleção")

class CollectionItemValuationDTO(BaseModel):
    card_id: UUID
    card_name: str
    quantity: int
    unit_price: Optional[Decimal] = None
    subtotal: Optional[Decimal] = None
    currency: str
    price_date: Optional[datetime] = None

class CollectionValuationResponseDTO(BaseModel):
    total_value: Decimal
    currency: str
    total_cards_count: int
    priced_items_count: int
    unpriced_items_count: int
    items: list[CollectionItemValuationDTO]