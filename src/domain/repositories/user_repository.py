from typing import Protocol, Optional
from uuid import UUID
from src.domain.entities.user import User

class UserRepository(Protocol):
    def find_by_id(self, user_id: UUID) -> Optional[User]:
        """Busca um usuário pelo seu ID interno."""
        ...

    def find_by_email(self, email: str) -> Optional[User]:
        """Busca um usuário pelo email para autenticação ou validação de duplicidade."""
        ...

    def save(self, user: User) -> None:
        """Persiste um novo usuário ou atualiza dados existentes."""
        ...