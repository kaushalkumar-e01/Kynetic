"""add_assessment_engine_columns_to_questions

Revision ID: c5d2e7f189ab
Revises: b4c19e8a7123
Create Date: 2026-11-06 22:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5d2e7f189ab'
down_revision: Union[str, None] = 'b4c19e8a7123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_cols = {c['name'] for c in insp.get_columns('questions')}
    existing_indexes = {ix['name'] for ix in insp.get_indexes('questions')}

    with op.batch_alter_table('questions') as batch_op:
        if 'category' not in existing_cols:
            batch_op.add_column(sa.Column('category', sa.String(length=100), server_default='cs_fundamentals', nullable=False))
        if 'subtopic' not in existing_cols:
            batch_op.add_column(sa.Column('subtopic', sa.String(length=100), nullable=True))
        if 'difficulty_level' not in existing_cols:
            batch_op.add_column(sa.Column('difficulty_level', sa.Integer(), server_default='2', nullable=False))
        if 'programming_language' not in existing_cols:
            batch_op.add_column(sa.Column('programming_language', sa.String(length=50), nullable=True))
        if 'source_name' not in existing_cols:
            batch_op.add_column(sa.Column('source_name', sa.String(length=100), server_default='Kynetic Original Bank', nullable=True))
        if 'source_license' not in existing_cols:
            batch_op.add_column(sa.Column('source_license', sa.String(length=100), server_default='CC-BY-4.0', nullable=True))
        if 'source_url' not in existing_cols:
            batch_op.add_column(sa.Column('source_url', sa.String(length=255), nullable=True))
        if 'validation_status' not in existing_cols:
            batch_op.add_column(sa.Column('validation_status', sa.String(length=50), server_default='validated', nullable=False))
        if 'version' not in existing_cols:
            batch_op.add_column(sa.Column('version', sa.Integer(), server_default='1', nullable=False))

        if 'ix_questions_category' not in existing_indexes:
            batch_op.create_index('ix_questions_category', ['category'], unique=False)
        if 'ix_questions_subtopic' not in existing_indexes:
            batch_op.create_index('ix_questions_subtopic', ['subtopic'], unique=False)
        if 'ix_questions_difficulty_level' not in existing_indexes:
            batch_op.create_index('ix_questions_difficulty_level', ['difficulty_level'], unique=False)
        if 'ix_questions_programming_language' not in existing_indexes:
            batch_op.create_index('ix_questions_programming_language', ['programming_language'], unique=False)
        if 'ix_questions_validation_status' not in existing_indexes:
            batch_op.create_index('ix_questions_validation_status', ['validation_status'], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    existing_cols = {c['name'] for c in insp.get_columns('questions')}
    existing_indexes = {ix['name'] for ix in insp.get_indexes('questions')}

    with op.batch_alter_table('questions') as batch_op:
        for idx in ['ix_questions_validation_status', 'ix_questions_programming_language', 'ix_questions_difficulty_level', 'ix_questions_subtopic', 'ix_questions_category']:
            if idx in existing_indexes:
                batch_op.drop_index(idx)

        for col in ['version', 'validation_status', 'source_url', 'source_license', 'source_name', 'programming_language', 'difficulty_level', 'subtopic', 'category']:
            if col in existing_cols:
                batch_op.drop_column(col)
