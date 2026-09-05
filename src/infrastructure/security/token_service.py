from datetime import datetime, timezone, timedelta
from typing import Any, Optional
import jwt
from src.infrastructure.config.settings import settings

class TokenService:
    def __init__(self) -> None:
        self._secret_key = settings.JWT_SECRET_KEY
        self._algorithm = settings.JWT_ALGORITHM
        self._expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES

    def create_access_token(self, subject: str, expires_delta: Optional[timedelta] = None) -> str:
        now = datetime.now(timezone.utc)
        expire = now + (expires_delta or timedelta(minutes=self._expire_minutes))
        
        # O padrão JWT define 'sub' como a identidade do sujeito (ID do usuário)
        payload: dict[str, Any] = {
            "sub": subject,
            "iat": now,
            "exp": expire
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def decode_access_token(self, token: str) -> Optional[dict[str, Any]]:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except jwt.PyJWTError:
            return None