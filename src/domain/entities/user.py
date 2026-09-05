from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class User:
    id: UUID
    email: str
    hashed_password: str
    created_at: datetime

    def __post_init__(self) -> None:
        # Eu valido que o email tenha formato minimamente válido e sem espaços
        self.email = self.email.strip().lower()
        if not self.email or "@" not in self.email:
            raise ValueError("O email informado é inválido.")
        if not self.hashed_password.strip():
            raise ValueError("O hash da senha não pode ser vazio.")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)