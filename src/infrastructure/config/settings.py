from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    POKEMON_TCG_API_KEY: str = ""
    
    KAFKA_BOOTSTRAP_SERVERS: str = "127.0.0.1:9092"
    KAFKA_TOPIC_PRICE_CHANGED: str = "price-changed"

    # Configurações de Autenticação JWT (Regra 4: Segurança)
    JWT_SECRET_KEY: str = "uma_chave_secreta_longa_e_aleatoria_para_o_desenvolvimento_local_2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()