"""userてーぶルのカラムis_activeのdefault値をfalseに変更

Revision ID: b0c8b0dc33b2
Revises: 7a06bc2cea27
Create Date: 2025-08-19 09:01:15.212769

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0c8b0dc33b2'
down_revision: Union[str, Sequence[str], None] = '7a06bc2cea27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
