from uuid import UUID
from pydantic import BaseModel, Field
from src.infrastructure.web.dtos.collection_dtos import CollectionValuationResponseDTO

class AddCardToPortfolioRequestDTO(BaseModel):
    card_id: UUID
    quantity: int = Field(gt=0, default=1, description="Quantidade da carta física a ser adicionada")