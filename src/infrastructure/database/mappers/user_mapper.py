from src.domain.entities.user import User
from src.infrastructure.database.models.user_model import UserModel

class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            hashed_password=entity.hashed_password,
            created_at=entity.created_at,
        )