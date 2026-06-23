from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_category_user_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    # Ícone/emoji e cor para a UI — ajudam na usabilidade e leitura rápida.
    icon: Mapped[str] = mapped_column(String(16), default="🏷️")
    color: Mapped[str] = mapped_column(String(16), default="#6366f1")
    # Exemplos de estabelecimentos para guiar a categorização automática da IA.
    examples: Mapped[str | None] = mapped_column(Text, nullable=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user = relationship("User", back_populates="categories")
