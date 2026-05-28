"""Ponto de entrada da API FastAPI do Finança Fácil."""
import logging
import warnings
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analysis, auth, budgets, categories, invoices, transactions
from app.core.config import settings
from app.core.database import init_db

logger = logging.getLogger("financa_facil")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    if settings.is_production and settings.SECRET_KEY.startswith("dev-only"):
        warnings.warn(
            "SECRET_KEY padrão de desenvolvimento em uso em produção! "
            "Defina a variável de ambiente SECRET_KEY.",
            stacklevel=1,
        )
    if not settings.ai_enabled:
        logger.info("OPENAI_API_KEY ausente — usando extrator heurístico e chat desativado.")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    description="API de gestão financeira pessoal com análise de faturas e IA.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (auth, categories, transactions, invoices, analysis, budgets):
    app.include_router(module.router, prefix=settings.API_PREFIX)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "ai_enabled": settings.ai_enabled}
