from pwdlib import PasswordHash

class PasswordService:
    def __init__(self) -> None:
        # Eu utilizo o algoritmo moderno Argon2id recomendado oficialmente pelo FastAPI
        self._hasher = PasswordHash.recommended()
        # Hash de mentira pré-calculado para defesa contra timing attacks
        self._dummy_hash = self._hasher.hash("dummy_password_for_timing_defense")

    def hash_password(self, plain_password: str) -> str:
        return self._hasher.hash(plain_password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self._hasher.verify(plain_password, hashed_password)

    def verify_dummy_password(self) -> None:
        # Eu executo uma verificação falsa proposital para igualar o tempo de processamento
        self._hasher.verify("dummy_password_for_timing_defense", self._dummy_hash)