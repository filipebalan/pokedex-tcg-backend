from dataclasses import dataclass, field
from uuid import UUID
from typing import Optional
from src.domain.value_objects.card_types import CardSupertype, EnergyType

@dataclass
class Card:
    id: UUID
    external_id: str
    name: str
    set_id: UUID
    card_number: str
    rarity: str
    supertype: CardSupertype
    types: list[EnergyType] = field(default_factory=list)
    hp: Optional[int] = None
    national_dex_number: Optional[int] = None

    def __post_init__(self) -> None:
        # Eu garanto que campos vitais de identificação não sejam vazios
        if not self.external_id.strip():
            raise ValueError("O identificador externo da carta não pode ser vazio.")
        if not self.name.strip():
            raise ValueError("O nome da carta não pode ser vazio.")
        if not self.card_number.strip():
            raise ValueError("O número da carta no Set não pode ser vazio.")

        # Eu valido a regra de negócio: Pokémon precisam ter HP positivo se informado
        if self.supertype == CardSupertype.POKEMON and self.hp is not None and self.hp <= 0:
            raise ValueError("O HP de uma carta de Pokémon deve ser estritamente maior que zero.")

    def is_pokemon(self) -> bool:
        # Método utilitário que expressa intenção clara no domínio
        return self.supertype == CardSupertype.POKEMON

    def __eq__(self, other: object) -> bool:
        # Igualdade estrita por identidade (ID)
        if not isinstance(other, Card):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)