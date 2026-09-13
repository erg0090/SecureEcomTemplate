"""split_professor_name_and_aggregate_weights

Revision ID: 50215f8eef99
Revises: d47f78b95361
Create Date: 2026-09-11 23:23:09.198327

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '50215f8eef99'
down_revision = 'd47f78b95361'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('professors', sa.Column('first_name', sa.String(), nullable=True))
    op.add_column('professors', sa.Column('last_name', sa.String(), nullable=True))
    op.add_column('courses', sa.Column('total_allocated_weight', sa.Float(), nullable=False, server_default='0.0'))

    op.execute(sa.text("""
        UPDATE courses AS c
        SET total_allocated_weight = COALESCE(
            (
                SELECT SUM(ct.weight)
                FROM course_tasks AS ct
                WHERE ct.course_id = c.id
            ),
            0.0
        )
    """))
    op.alter_column('courses', 'total_allocated_weight', server_default=None)

    # Preserve the original name by splitting the first token from the remainder.
    op.execute(sa.text("""
        UPDATE professors
        SET first_name = NULLIF(split_part(trim(professor_name), ' ', 1), ''),
            last_name = NULLIF(
                regexp_replace(trim(professor_name), '^\\S+\\s*', ''),
                ''
            )
        WHERE professor_name IS NOT NULL
    """))

    op.drop_constraint('uq_professor_name', 'professors', type_='unique')
    op.drop_column('professors', 'professor_name')


def downgrade():
    op.drop_column('courses', 'total_allocated_weight')
    op.add_column('professors', sa.Column('professor_name', sa.String(), nullable=True))
    op.execute(sa.text("""
        UPDATE professors
        SET professor_name = NULLIF(
            concat_ws(' ', NULLIF(trim(first_name), ''), NULLIF(trim(last_name), '')),
            ''
        )
    """))
    op.alter_column('professors', 'professor_name', nullable=False)
    op.create_unique_constraint('uq_professor_name', 'professors', ['professor_name'])
    op.drop_column('professors', 'last_name')
    op.drop_column('professors', 'first_name')
