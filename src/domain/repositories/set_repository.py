from typing import Protocol, Optional
from uuid import UUID
from src.domain.entities.set import Set

class SetRepository(Protocol):
    def find_by_id(self, set_id: UUID) -> Optional[Set]:
        """Busca uma coleção pelo seu ID interno do nosso sistema."""
        ...

    def find_by_external_id(self, external_id: str) -> Optional[Set]:
        """Busca uma coleção pelo ID da API externa (ex: 'base1', 'sv01') para garantir idempotência."""
        ...

    def save(self, collection_set: Set) -> None:
        """Persiste ou atualiza uma coleção no banco de dados (Upsert idempotente)."""
        ...