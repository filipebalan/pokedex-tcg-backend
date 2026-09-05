from typing import Optional
from src.domain.repositories.user_repository import UserRepository
from src.infrastructure.security.password_service import PasswordService
from src.infrastructure.security.token_service import TokenService

class AuthenticateUserUseCase:
    def __init__(
        self,
        user_repo: UserRepository,
        password_service: PasswordService,
        token_service: TokenService
    ) -> None:
        self._user_repo = user_repo
        self._password_service = password_service
        self._token_service = token_service

    async def execute(self, email: str, plain_password: str) -> Optional[str]:
        clean_email = email.strip().lower()
        user = await self._user_repo.find_by_email(clean_email)

        # Se o usuário não existir, eu rodo a checagem falsa para defesa contra timing attacks
        if not user:
            self._password_service.verify_dummy_password()
            return None

        # Se a senha estiver incorreta
        if not self._password_service.verify_password(plain_password, user.hashed_password):
            return None

        # Eu emito o token JWT contendo o ID do usuário como 'sub'
        return self._token_service.create_access_token(subject=str(user.id))