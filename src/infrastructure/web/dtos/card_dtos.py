from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict

class CardResponseDTO(BaseModel):
    # Eu configuro o Pydantic v2 para permitir serialização a partir de atributos de objetos
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    external_id: str
    name: str
    set_id: UUID
    card_number: str
    rarity: str
    supertype: str
    types: list[str]
    hp: Optional[int] = None
    national_dex_number: Optional[int] = None

class PaginatedCardsResponseDTO(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[CardResponseDTO]