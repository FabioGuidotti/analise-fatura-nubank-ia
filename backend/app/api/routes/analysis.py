"""Rotas de análise financeira, recomendações e chat com IA."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.analysis import (
    AnalysisResponse,
    ChatRequest,
    ChatResponse,
)
from app.services import ai_service, analysis_service, recommendation_service

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _load_transactions(db: Session, user: User) -> list[Transaction]:
    return db.query(Transaction).filter(Transaction.user_id == user.id).all()


@router.get("", response_model=AnalysisResponse)
def get_analysis(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    txs = _load_transactions(db, user)
    budgets = db.query(Budget).filter(Budget.user_id == user.id).all()

    return AnalysisResponse(
        summary=analysis_service.build_summary(txs),
        by_category=analysis_service.by_category(txs),
        by_month=analysis_service.by_month(txs),
        by_weekday=analysis_service.by_weekday(txs),
        top_merchants=analysis_service.top_merchants(txs),
        recurring=analysis_service.recurring_expenses(txs),
        recommendations=recommendation_service.generate(txs, budgets),
    )


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    txs = _load_transactions(db, user)
    if payload.category:
        txs = [t for t in txs if t.category == payload.category]

    context = _build_chat_context(txs)
    answer = ai_service.chat(payload.question, context)
    return ChatResponse(answer=answer)


def _build_chat_context(txs: list[Transaction]) -> str:
    if not txs:
        return "O usuário ainda não importou nenhuma transação."

    summary = analysis_service.build_summary(txs)
    categories = analysis_service.by_category(txs)
    top = analysis_service.top_merchants(txs, limit=8)

    lines = [
        f"Total gasto: R$ {summary['total_spent']:.2f}",
        f"Nº de transações: {summary['transaction_count']}",
        f"Ticket médio: R$ {summary['average_transaction']:.2f}",
        f"Período: {summary['period_start']} a {summary['period_end']}",
        "",
        "Gastos por categoria:",
    ]
    lines += [
        f"- {c['category']}: R$ {c['total']:.2f} ({c['percentage']:.1f}%)"
        for c in categories
    ]
    lines.append("")
    lines.append("Maiores estabelecimentos:")
    lines += [f"- {m['description']}: R$ {m['total']:.2f} ({m['count']}x)" for m in top]
    return "\n".join(lines)
