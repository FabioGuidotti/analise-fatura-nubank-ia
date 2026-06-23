"""Importa todos os modelos para que sejam registrados na metadata do SQLAlchemy."""
from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User

__all__ = ["User", "Category", "Transaction", "Budget"]
