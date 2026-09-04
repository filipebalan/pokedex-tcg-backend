from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Eu configuro o Pydantic para ler o arquivo .env na raiz do projeto
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    POKEMON_TCG_API_KEY: str = ""

# Instância singleton que usaremos em toda a infraestrutura
settings = Settings()