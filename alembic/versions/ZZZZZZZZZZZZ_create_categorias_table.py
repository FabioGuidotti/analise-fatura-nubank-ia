"""create categorias table

Revision ID: ZZZZZZZZZZZZ
Revises: YYYYYYYYYYYY
Create Date: YYYY-MM-DD HH:MM:SS.ZZZZZZ

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = 'ZZZZZZZZZZZZ'
down_revision = 'YYYYYYYYYYYY'
branch_labels = None
depends_on = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()
    
    if 'categorias' not in tables:
        op.create_table(
            'categorias',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('nome', sa.String, unique=True, nullable=False)
        )
        
        # Preencher a tabela de categorias com as categorias existentes nas transações
        conn.execute(text("""
            INSERT INTO categorias (nome)
            SELECT DISTINCT categoria FROM transacoes
            WHERE categoria IS NOT NULL AND categoria != ''
        """))
    else:
        print("A tabela 'categorias' já existe. Pulando a criação.")

def downgrade() -> None:
    op.drop_table('categorias')