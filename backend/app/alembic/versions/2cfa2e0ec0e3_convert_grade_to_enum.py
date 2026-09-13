"""convert_grade_to_enum

Revision ID: 2cfa2e0ec0e3
Revises: 6dac1bf03fd0
Create Date: 2026-09-11 18:52:54.534427

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '2cfa2e0ec0e3'
down_revision = '6dac1bf03fd0'
branch_labels = None
depends_on = None


def upgrade():
    grade_letter_enum = sa.Enum(
        'A', 'B', 'C', 'D', 'F', 'W', 'I', name='grade_letter_enum'
    )
    grade_letter_enum.create(op.get_bind(), checkfirst=False)
    op.add_column(
        'courses',
        sa.Column('grade', grade_letter_enum, nullable=True),
    )


def downgrade():
    op.drop_column('courses', 'grade')
    grade_letter_enum = sa.Enum(
        'A', 'B', 'C', 'D', 'F', 'W', 'I', name='grade_letter_enum'
    )
    grade_letter_enum.drop(op.get_bind(), checkfirst=False)
