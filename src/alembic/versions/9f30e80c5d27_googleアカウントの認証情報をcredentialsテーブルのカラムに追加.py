"""googleアカウントの認証情報をcredentialsテーブルのカラムに追加

Revision ID: 9f30e80c5d27
Revises: b0c8b0dc33b2
Create Date: 2025-09-01 08:53:47.129166

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f30e80c5d27'
down_revision: Union[str, Sequence[str], None] = 'b0c8b0dc33b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
