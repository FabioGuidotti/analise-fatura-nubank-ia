"""Importação de faturas em PDF com extração inteligente e preview seguro.

O fluxo é "anti-burro": o upload apenas EXTRAI e devolve um preview com
detecção de duplicatas. Nada é salvo até o usuário confirmar (POST em
/transactions). Assim o usuário sempre revisa antes de gravar.
"""
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import ImportPreviewItem, ImportResult
from app.services import ai_service, pdf_service

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/preview", response_model=ImportResult)
async def preview_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF.")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="Arquivo muito grande (máx. 10 MB).")
    if not content:
        raise HTTPException(status_code=400, detail="Arquivo vazio.")

    text = pdf_service.extract_text(content)
    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="Não foi possível extrair texto do PDF. Verifique o arquivo.",
        )

    categories = [
        {"name": c.name, "examples": c.examples}
        for c in db.query(Category).filter(Category.user_id == user.id).all()
    ]

    extracted: list[dict] = []
    for chunk in pdf_service.chunk_text(text):
        extracted.extend(ai_service.extract_transactions(chunk, categories))

    if not extracted:
        raise HTTPException(
            status_code=422,
            detail="Nenhuma transação encontrada na fatura.",
        )

    # Detecção de duplicatas contra o que já está salvo.
    existing = {
        (t.date, t.description.lower(), round(t.amount, 2))
        for t in db.query(Transaction).filter(Transaction.user_id == user.id).all()
    }

    items: list[ImportPreviewItem] = []
    duplicates = 0
    seen_in_batch: set = set()
    for tx in extracted:
        key = (tx["date"], tx["description"].lower(), round(tx["amount"], 2))
        is_dup = key in existing or key in seen_in_batch
        seen_in_batch.add(key)
        if is_dup:
            duplicates += 1
        items.append(ImportPreviewItem(**tx, duplicate=is_dup))

    return ImportResult(
        source_file=file.filename or "fatura.pdf",
        items=items,
        total_amount=round(sum(i.amount for i in items), 2),
        duplicates=duplicates,
    )
