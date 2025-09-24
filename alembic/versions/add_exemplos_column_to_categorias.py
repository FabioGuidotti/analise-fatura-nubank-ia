"""add exemplos column to categorias

Revision ID: add_exemplos_column
Revises: 3fdfe1a91380
Create Date: 2024-12-19 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_exemplos_column'
down_revision: Union[str, None] = '3fdfe1a91380'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Adicionar coluna exemplos à tabela categorias
    op.add_column('categorias', sa.Column('exemplos', sa.String(), nullable=True))

def downgrade():
    # Remover coluna exemplos da tabela categorias
    op.drop_column('categorias', 'exemplos')
