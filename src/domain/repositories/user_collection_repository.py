from typing import Protocol, Optional
from uuid import UUID
from src.domain.entities.user_collection import UserCollection

class UserCollectionRepository(Protocol):
    def find_by_user_id(self, user_id: UUID) -> Optional[UserCollection]:
        """Busca a coleção cadastrada para determinado usuário."""
        ...

    def save(self, collection: UserCollection) -> None:
        """Persiste ou atualiza a coleção e todos os seus itens associados."""
        ...