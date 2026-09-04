from dataclasses import dataclass
from datetime import date
from uuid import UUID

# Em uma Entity, eu não utilizo frozen=True porque entidades têm ciclo de vida
# e seus metadados podem ser corrigidos ou atualizados no tempo.
@dataclass
class Set:
    id: UUID
    external_id: str
    name: str
    series: str
    release_date: date
    total_cards: int

    def __post_init__(self) -> None:
        # Eu valido as invariantes obrigatórias de domínio para uma coleção
        if not self.external_id.strip():
            raise ValueError("O identificador externo do Set não pode ser vazio.")
        if not self.name.strip():
            raise ValueError("O nome do Set não pode ser vazio.")
        if self.total_cards <= 0:
            raise ValueError("O total de cartas de um Set deve ser estritamente maior que zero.")

    def __eq__(self, other: object) -> bool:
        # No DDD, a igualdade de uma Entity é estritamente definida pela sua identidade (ID)
        if not isinstance(other, Set):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)