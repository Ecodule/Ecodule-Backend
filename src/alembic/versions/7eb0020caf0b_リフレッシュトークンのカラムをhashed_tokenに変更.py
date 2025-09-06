"""リフレッシュトークンのカラムをhashed_tokenに変更

Revision ID: 7eb0020caf0b
Revises: 9d2a01d1d018
Create Date: 2025-09-06 15:12:00.776358

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7eb0020caf0b'
down_revision: Union[str, Sequence[str], None] = '9d2a01d1d018'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 'token' カラムを 'hashed_token' にリネーム
    op.alter_column(
        'refresh_tokens',  # テーブル名
        'token',           # 変更前のカラム名
        new_column_name='hashed_token' # 変更後のカラム名
    )


def downgrade() -> None:
    op.alter_column(
        'refresh_tokens',  # テーブル名
        'hashed_token',    # 変更前のカラム名
        new_column_name='token' # 変更後のカラム名
    )
