from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

@dataclass
class UserCollectionItem:
    card_id: UUID
    quantity: int
    added_at: datetime

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("A quantidade de cartas deve ser estritamente maior que zero.")

@dataclass
class UserCollection:
    id: UUID
    user_id: UUID
    name: str = "Minha Coleção"
    items: list[UserCollectionItem] = field(default_factory=list)

    def add_or_update_card(self, card_id: UUID, quantity: int) -> None:
        # Se a carta já estiver na coleção, eu somo a quantidade; senão, adiciono novo item
        for item in self.items:
            if item.card_id == card_id:
                item.quantity += quantity
                return

        self.items.append(
            UserCollectionItem(
                card_id=card_id,
                quantity=quantity,
                added_at=datetime.now(timezone.utc)
            )
        )

    def remove_card(self, card_id: UUID) -> None:
        self.items = [item for item in self.items if item.card_id != card_id]