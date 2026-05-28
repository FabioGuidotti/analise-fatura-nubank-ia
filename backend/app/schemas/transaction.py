from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    date: date
    description: str = Field(min_length=1, max_length=255)
    amount: float
    category: str = Field(default="Outros", max_length=80)


class TransactionCreate(TransactionBase):
    source_file: Optional[str] = None


class TransactionUpdate(BaseModel):
    date: Optional[date] = None
    description: Optional[str] = Field(default=None, max_length=255)
    amount: Optional[float] = None
    category: Optional[str] = Field(default=None, max_length=80)


class TransactionPublic(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    source_file: Optional[str] = None


class ImportPreviewItem(TransactionBase):
    """Item extraído de uma fatura, ainda não persistido."""
    duplicate: bool = False


class ImportResult(BaseModel):
    source_file: str
    items: list[ImportPreviewItem]
    total_amount: float
    duplicates: int
