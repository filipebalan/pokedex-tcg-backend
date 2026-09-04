from typing import Protocol, Optional
from uuid import UUID
from src.domain.entities.card import Card

class CardRepository(Protocol):
    def find_by_id(self, card_id: UUID) -> Optional[Card]:
        """Busca uma carta pelo seu ID interno."""
        ...

    def find_by_external_id(self, external_id: str) -> Optional[Card]:
        """Busca uma carta pelo ID externo (ex: 'base1-4') para evitar duplicações no sync."""
        ...

    def list_cards(
        self,
        set_id: Optional[UUID] = None,
        name: Optional[str] = None,
        rarity: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Card]:
        """Lista cartas aplicando filtros opcionais e paginação para performance."""
        ...

    def save(self, card: Card) -> None:
        """Persiste ou atualiza uma carta no banco de dados (Upsert idempotente)."""
        ...