"""create transacoes table

Revision ID: XXXXXXXXXXXX
Revises: 
Create Date: YYYY-MM-DD HH:MM:SS.ZZZZZZ

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'XXXXXXXXXXXX'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    
    if 'transacoes' not in tables:
        op.create_table(
            'transacoes',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('data', sa.Date),
            sa.Column('descricao', sa.String),
            sa.Column('valor', sa.Float),
            sa.Column('categoria', sa.String)
        )
    else:
        print("A tabela 'transacoes' já existe. Pulando a criação.")

def downgrade() -> None:
    op.drop_table('transacoes')