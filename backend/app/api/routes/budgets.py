from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetPublic, BudgetStatus
from app.services import analysis_service

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("", response_model=list[BudgetPublic])
def list_budgets(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return db.query(Budget).filter(Budget.user_id == user.id).all()


@router.put("", response_model=BudgetPublic)
def upsert_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Cria ou atualiza o orçamento de uma categoria (idempotente)."""
    budget = (
        db.query(Budget)
        .filter(Budget.user_id == user.id, Budget.category == payload.category)
        .first()
    )
    if budget:
        budget.monthly_limit = payload.monthly_limit
    else:
        budget = Budget(user_id=user.id, **payload.model_dump())
        db.add(budget)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflito ao salvar orçamento.")
    db.refresh(budget)
    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == user.id)
        .first()
    )
    if budget is None:
        raise HTTPException(status_code=404, detail="Orçamento não encontrado.")
    db.delete(budget)
    db.commit()


@router.get("/status", response_model=list[BudgetStatus])
def budget_status(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    """Acompanhamento do orçamento do mês corrente por categoria."""
    budgets = db.query(Budget).filter(Budget.user_id == user.id).all()
    txs = db.query(Transaction).filter(Transaction.user_id == user.id).all()
    spent = analysis_service.current_month_spending_by_category(txs)

    result: list[BudgetStatus] = []
    for b in budgets:
        used = spent.get(b.category, 0.0)
        pct = (used / b.monthly_limit * 100) if b.monthly_limit else 0.0
        if pct >= 100:
            state = "exceeded"
        elif pct >= 80:
            state = "warning"
        else:
            state = "ok"
        result.append(
            BudgetStatus(
                category=b.category,
                monthly_limit=b.monthly_limit,
                spent=round(used, 2),
                remaining=round(b.monthly_limit - used, 2),
                percentage=round(pct, 1),
                status=state,
            )
        )
    return result
