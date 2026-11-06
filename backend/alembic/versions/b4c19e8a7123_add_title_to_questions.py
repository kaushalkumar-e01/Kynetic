"""add_title_to_questions

Revision ID: b4c19e8a7123
Revises: a3f24cacf581
Create Date: 2026-11-06 17:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4c19e8a7123'
down_revision: Union[str, None] = 'a3f24cacf581'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('questions', sa.Column('title', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('questions', 'title')

