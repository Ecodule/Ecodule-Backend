"""googleアカウントの認証情報をcredentialsテーブルのカラムに追加

Revision ID: b6512adf5d99
Revises: 9f30e80c5d27
Create Date: 2025-09-01 08:55:37.995192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b6512adf5d99'
down_revision: Union[str, Sequence[str], None] = '9f30e80c5d27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
