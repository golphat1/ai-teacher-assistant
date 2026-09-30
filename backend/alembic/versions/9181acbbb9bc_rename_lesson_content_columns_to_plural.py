"""rename lesson content columns to plural

Revision ID: 9181acbbb9bc
Revises: a76ee0ac044b
Create Date: 2026-09-28 21:34:53.003936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9181acbbb9bc'
down_revision: Union[str, None] = 'a76ee0ac044b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
     op.alter_column("lesson_contents", "learning_objective", new_column_name="learning_objectives")
     op.alter_column("lesson_contents", "teaching_activity", new_column_name="teaching_activities")


def downgrade() -> None:
    op.alter_column("lesson_contents", "learning_objectives", new_column_name="learning_objective")
    op.alter_column("lesson_contents", "teaching_activities", new_column_name="teaching_activity")
