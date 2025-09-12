"""カテゴリーテーブルにマスタデータを挿入

Revision ID: b79dc12df5c9
Revises: fb5a5493d1c5
Create Date: 2025-09-12 05:18:32.128799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision: str = 'b79dc12df5c9'
down_revision: Union[str, Sequence[str], None] = 'fb5a5493d1c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    categories_table = sa.Table('categories',
        sa.MetaData(),
        sa.Column('category_id', sa.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_name', sa.String(), nullable=False, unique=True)
    )

    op.bulk_insert(categories_table,
        [
            {'category_id': uuid.uuid4(), 'category_name': 'ゴミ出し'},
            {'category_id': uuid.uuid4(), 'category_name': '通勤・通学'},
            {'category_id': uuid.uuid4(), 'category_name': '外出'},
            {'category_id': uuid.uuid4(), 'category_name': '買い物'},
        ]
    )

def downgrade() -> None:
    # downgrade時にはデータを削除する
    op.execute("DELETE FROM categories")
