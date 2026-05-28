"""Configuração do SQLAlchemy: engine, sessão e Base declarativa."""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Para SQLite precisamos de check_same_thread=False ao usar múltiplas threads
# (o servidor ASGI). Para outros bancos a opção é ignorada.
connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base declarativa para todos os modelos ORM."""


def get_db() -> Generator:
    """Dependência FastAPI que entrega uma sessão e garante o fechamento."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Cria as tabelas. Importa os modelos para registrá-los na metadata."""
    from app import models  # noqa: F401  (efeito colateral: registra os modelos)

    Base.metadata.create_all(bind=engine)
