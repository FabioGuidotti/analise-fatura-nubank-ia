"""Primeira execução

Revision ID: f4caec97700b
Revises: 
Create Date: 2024-09-25 22:13:50.753506

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'f4caec97700b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Criação da tabela categorias
    op.create_table('categorias',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nome')
    )

    # Criação da tabela transacoes
    op.create_table('transacoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data', sa.Date(), nullable=True),
        sa.Column('descricao', sa.String(), nullable=True),
        sa.Column('valor', sa.Float(), nullable=True),
        sa.Column('categoria', sa.String(), nullable=True),
        sa.Column('arquivo_origem', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Inserir a categoria 'Outros'
    op.execute("INSERT INTO categorias (nome) VALUES ('Outros')")

def downgrade():
    op.drop_table('transacoes')
    op.drop_table('categorias')
