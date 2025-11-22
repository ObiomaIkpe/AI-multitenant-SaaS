"""add_query_logs_table

Revision ID: 0714992e241d
Revises: e823a1decfb3
Create Date: 2025-11-22 10:39:09.420913

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0714992e241d'
down_revision: Union[str, Sequence[str], None] = 'e823a1decfb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'query_logs',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('tenant_id', sa.String(), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('filters_applied', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('answer_length', sa.Integer(), nullable=True),
        sa.Column('sources_count', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_query_logs_tenant_id', 'query_logs', ['tenant_id'])
    op.create_foreign_key(None, 'query_logs', 'tenants', ['tenant_id'], ['id'])

def downgrade() -> None:
    op.drop_table('query_logs')