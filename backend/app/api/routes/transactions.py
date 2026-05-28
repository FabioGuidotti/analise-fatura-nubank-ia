from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionPublic,
    TransactionUpdate,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _query(db: Session, user: User):
    return db.query(Transaction).filter(Transaction.user_id == user.id)


@router.get("", response_model=list[TransactionPublic])
def list_transactions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    category: Optional[str] = None,
    start: Optional[date] = None,
    end: Optional[date] = None,
    min_amount: Optional[float] = None,
    source_file: Optional[str] = None,
):
    query = _query(db, user)
    if category:
        query = query.filter(Transaction.category == category)
    if start:
        query = query.filter(Transaction.date >= start)
    if end:
        query = query.filter(Transaction.date <= end)
    if min_amount is not None:
        query = query.filter(Transaction.amount >= min_amount)
    if source_file:
        query = query.filter(Transaction.source_file == source_file)
    return query.order_by(Transaction.date.desc()).all()


@router.post("", response_model=list[TransactionPublic], status_code=status.HTTP_201_CREATED)
def create_transactions(
    payload: list[TransactionCreate],
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Cria uma ou várias transações (usado ao confirmar uma importação)."""
    created: list[Transaction] = []
    for item in payload:
        tx = Transaction(user_id=user.id, **item.model_dump())
        db.add(tx)
        created.append(tx)
    db.commit()
    for tx in created:
        db.refresh(tx)
    return created


def _get_owned(db: Session, user: User, tx_id: int) -> Transaction:
    tx = _query(db, user).filter(Transaction.id == tx_id).first()
    if tx is None:
        raise HTTPException(status_code=404, detail="Transação não encontrada.")
    return tx


@router.put("/{tx_id}", response_model=TransactionPublic)
def update_transaction(
    tx_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tx = _get_owned(db, user, tx_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tx, field, value)
    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    tx_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    tx = _get_owned(db, user, tx_id)
    db.delete(tx)
    db.commit()


@router.delete("", status_code=status.HTTP_200_OK)
def bulk_delete(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    source_file: Optional[str] = Query(default=None),
    all: bool = Query(default=False),
):
    """Exclusão em massa por arquivo de origem ou de todos os dados."""
    query = _query(db, user)
    if source_file:
        query = query.filter(Transaction.source_file == source_file)
    elif not all:
        raise HTTPException(
            status_code=400,
            detail="Informe 'source_file' ou 'all=true' para exclusão em massa.",
        )
    deleted = query.delete(synchronize_session=False)
    db.commit()
    return {"deleted": deleted}


@router.get("/source-files", response_model=list[str])
def list_source_files(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    rows = (
        _query(db, user)
        .with_entities(Transaction.source_file)
        .distinct()
        .all()
    )
    return [r[0] for r in rows if r[0]]
