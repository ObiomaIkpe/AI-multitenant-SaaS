"""add_document_metadata_fields

Revision ID: 3631356afe74
Revises: 96b2a441a7a1
Create Date: 2025-11-22 01:29:58.188340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3631356afe74'
down_revision: Union[str, Sequence[str], None] = '96b2a441a7a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
