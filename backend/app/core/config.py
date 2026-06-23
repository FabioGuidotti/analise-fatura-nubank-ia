"""Configuração central da aplicação carregada de variáveis de ambiente.

Nenhum segredo é hardcoded. Em produção, defina ao menos SECRET_KEY e
OPENAI_API_KEY no ambiente (ou em um arquivo .env).
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Aplicação ---
    APP_NAME: str = "Finança Fácil"
    ENVIRONMENT: str = "development"  # development | production
    API_PREFIX: str = "/api"

    # --- Segurança / JWT ---
    # Em produção isto DEVE vir do ambiente. O valor padrão só serve para
    # desenvolvimento local e dispara um aviso no startup.
    SECRET_KEY: str = "dev-only-insecure-key-change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Limite de tentativas de login antes do bloqueio temporário
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15

    # --- Banco de dados ---
    # Por padrão usa SQLite (zero configuração). Para PostgreSQL defina
    # DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db
    DATABASE_URL: str = "sqlite:///./financa_facil.db"

    # --- CORS ---
    # Origens permitidas para o frontend (separadas por vírgula). Mantido como
    # string para evitar o parsing JSON automático do pydantic-settings em
    # campos de tipo lista lidos de variáveis de ambiente.
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # --- OpenAI ---
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_EXTRACTION: str = "gpt-4o-mini"
    OPENAI_MODEL_CHAT: str = "gpt-4o-mini"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def ai_enabled(self) -> bool:
        return bool(self.OPENAI_API_KEY)

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
