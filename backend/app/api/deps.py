"""Dependências compartilhadas das rotas: usuário autenticado e rate limiting."""
import time
from collections import defaultdict

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import TOKEN_TYPE_ACCESS, decode_token
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise invalid

    payload = decode_token(credentials.credentials, expected_type=TOKEN_TYPE_ACCESS)
    if not payload:
        raise invalid

    user = db.get(User, int(payload["sub"]))
    if user is None or not user.is_active:
        raise invalid
    return user


class RateLimiter:
    """Rate limiter simples em memória (janela deslizante por chave).

    Suficiente para proteger endpoints sensíveis (login/registro) em uma única
    instância. Em produção multi-instância, troque por Redis.
    """

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str) -> None:
        now = time.time()
        hits = [t for t in self._hits[key] if now - t < self.window]
        if len(hits) >= self.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas tentativas. Aguarde alguns minutos e tente novamente.",
            )
        hits.append(now)
        self._hits[key] = hits


# 10 tentativas de autenticação por IP a cada 5 minutos.
auth_rate_limiter = RateLimiter(max_requests=10, window_seconds=300)
