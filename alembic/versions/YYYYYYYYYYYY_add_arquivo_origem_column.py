"""add arquivo_origem column

Revision ID: YYYYYYYYYYYY
Revises: XXXXXXXXXXXX
Create Date: YYYY-MM-DD HH:MM:SS.ZZZZZZ

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'YYYYYYYYYYYY'
down_revision = 'XXXXXXXXXXXX'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column('transacoes', sa.Column('arquivo_origem', sa.String))

def downgrade() -> None:
    op.drop_column('transacoes', 'arquivo_origem')