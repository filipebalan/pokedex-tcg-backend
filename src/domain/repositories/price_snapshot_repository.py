from typing import Protocol
from uuid import UUID
from datetime import datetime
from src.domain.value_objects.card_types import PriceSnapshot

class PriceSnapshotRepository(Protocol):
    def save(self, snapshot: PriceSnapshot) -> None:
        """Persiste um novo registro temporal de preço (operação estritamente append-only)."""
        ...

    def list_by_card_id(
        self,
        card_id: UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> list[PriceSnapshot]:
        """Retorna a série temporal ordenada por data (pronta para gerar gráficos)."""
        ...

    def find_latest_by_card_id(self, card_id: UUID) -> Optional[PriceSnapshot]:
        """Busca o snapshot de preço mais recente da carta."""
        ...