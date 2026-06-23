"""Categorias padrão criadas automaticamente para novos usuários.

Faz parte da estratégia "vida fácil / anti-burro": o usuário já começa com um
conjunto sensato de categorias e exemplos, sem precisar configurar nada.
"""
from sqlalchemy.orm import Session

from app.models.category import Category

DEFAULT_CATEGORIES = [
    {"name": "Alimentação", "icon": "🍽️", "color": "#f59e0b",
     "examples": "Restaurante, Padaria, Lanchonete, iFood, Delivery"},
    {"name": "Mercado", "icon": "🛒", "color": "#10b981",
     "examples": "Supermercado, Hortifruti, Açougue, Atacadão"},
    {"name": "Transporte", "icon": "🚗", "color": "#3b82f6",
     "examples": "Uber, 99, Combustível, Posto, Estacionamento, Metrô"},
    {"name": "Moradia", "icon": "🏠", "color": "#8b5cf6",
     "examples": "Aluguel, Condomínio, Luz, Água, Gás, Internet"},
    {"name": "Saúde", "icon": "💊", "color": "#ef4444",
     "examples": "Farmácia, Plano de saúde, Consulta, Exame, Academia"},
    {"name": "Lazer", "icon": "🎬", "color": "#ec4899",
     "examples": "Cinema, Streaming, Netflix, Spotify, Show, Viagem"},
    {"name": "Compras", "icon": "🛍️", "color": "#06b6d4",
     "examples": "Roupas, Eletrônicos, Amazon, Mercado Livre, Shopping"},
    {"name": "Educação", "icon": "📚", "color": "#6366f1",
     "examples": "Curso, Livro, Faculdade, Material escolar"},
    {"name": "Serviços", "icon": "🔧", "color": "#64748b",
     "examples": "Assinatura, Software, Telefonia, Banco, Taxa"},
    {"name": "Outros", "icon": "🏷️", "color": "#94a3b8", "examples": ""},
]


def seed_default_categories(db: Session, user_id: int) -> None:
    for cat in DEFAULT_CATEGORIES:
        db.add(Category(user_id=user_id, **cat))
    db.commit()
