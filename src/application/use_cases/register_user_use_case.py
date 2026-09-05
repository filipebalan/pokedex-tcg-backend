from uuid import uuid4
from datetime import datetime, timezone
from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.security.password_service import PasswordService

class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository, password_service: PasswordService) -> None:
        self._user_repo = user_repo
        self._password_service = password_service

    async def execute(self, email: str, plain_password: str) -> User:
        clean_email = email.strip().lower()

        # 1. Eu valido regras de negócio para a senha
        if len(plain_password) < 8:
            raise ValueError("A senha deve conter no mínimo 8 caracteres.")

        # 2. Eu valido se o email já está cadastrado
        existing = await self._user_repo.find_by_email(clean_email)
        if existing:
            raise ValueError("Email já cadastrado no sistema.")

        # 3. Eu gero o hash seguro com Argon2id
        hashed = self._password_service.hash_password(plain_password)

        new_user = User(
            id=uuid4(),
            email=clean_email,
            hashed_password=hashed,
            created_at=datetime.now(timezone.utc)
        )

        await self._user_repo.save(new_user)
        return new_user