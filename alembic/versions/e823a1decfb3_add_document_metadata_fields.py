"""add_document_metadata_fields

Revision ID: e823a1decfb3
Revises: 3631356afe74
Create Date: 2025-11-22 02:15:04.498303

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e823a1decfb3'
down_revision: Union[str, Sequence[str], None] = '3631356afe74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add metadata fields to documents table."""
    
    # Add category column (nullable string with index)
    op.add_column('documents', sa.Column('category', sa.String(), nullable=True))
    
    # Add tags column (JSON array, defaults to empty list)
    op.add_column('documents', sa.Column('tags', sa.JSON(), nullable=False, server_default='[]'))
    
    # Add description column (nullable text)
    op.add_column('documents', sa.Column('description', sa.Text(), nullable=True))
    
    # Create index on category for faster filtering
    op.create_index('ix_documents_category', 'documents', ['category'], unique=False)


def downgrade() -> None:
    """Downgrade schema - Remove metadata fields from documents table."""
    
    # Remove index first
    op.drop_index('ix_documents_category', table_name='documents')
    
    # Remove columns in reverse order
    op.drop_column('documents', 'description')
    op.drop_column('documents', 'tags')
    op.drop_column('documents', 'category')
