"""fill_data_tables

Revision ID: d47f78b95361
Revises: 2cfa2e0ec0e3
Create Date: 2026-09-11 20:17:23.228672

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'd47f78b95361'
down_revision = '2cfa2e0ec0e3'
branch_labels = None
depends_on = None


def upgrade():
    grade_letter_enum = sa.Enum(
        'A', 'B', 'C', 'D', 'F', 'W', 'I', name='grade_letter_enum'
    )
    professors = sa.table(
        'professors',
        sa.column('id', sa.Uuid()),
        sa.column('professor_name', sa.String()),
    )
    terms = sa.table(
        'terms',
        sa.column('id', sa.Uuid()),
        sa.column('semester_name', sa.String()),
        sa.column('academic_year', sa.Integer()),
    )
    courses = sa.table(
        'courses',
        sa.column('id', sa.Uuid()),
        sa.column('course_code', sa.String()),
        sa.column('title', sa.String()),
        sa.column('term_id', sa.Uuid()),
        sa.column('professor_id', sa.Uuid()),
        sa.column('grade', grade_letter_enum),
    )
    course_tasks = sa.table(
        'course_tasks',
        sa.column('id', sa.Uuid()),
        sa.column('task_title', sa.String()),
        sa.column('weight', sa.Float()),
        sa.column('course_id', sa.Uuid()),
    )

    op.bulk_insert(
        professors,
        [
            {'id': '10000000-0000-0000-0000-000000000001', 'professor_name': 'Ada Lovelace'},
            {'id': '10000000-0000-0000-0000-000000000002', 'professor_name': 'Alan Turing'},
            {'id': '10000000-0000-0000-0000-000000000003', 'professor_name': 'Grace Hopper'},
        ],
    )
    op.bulk_insert(
        terms,
        [
            {'id': '20000000-0000-0000-0000-000000000001', 'semester_name': 'Fall', 'academic_year': 2026},
            {'id': '20000000-0000-0000-0000-000000000002', 'semester_name': 'Spring', 'academic_year': 2027},
        ],
    )
    op.bulk_insert(
        courses,
        [
            {
                'id': '30000000-0000-0000-0000-000000000001',
                'course_code': 'CSCE 4560',
                'title': 'Software Engineering',
                'term_id': '20000000-0000-0000-0000-000000000001',
                'professor_id': '10000000-0000-0000-0000-000000000001',
                'grade': 'A',
            },
            {
                'id': '30000000-0000-0000-0000-000000000002',
                'course_code': 'CSCE 4110',
                'title': 'Operating Systems',
                'term_id': '20000000-0000-0000-0000-000000000001',
                'professor_id': '10000000-0000-0000-0000-000000000002',
                'grade': 'B',
            },
            {
                'id': '30000000-0000-0000-0000-000000000003',
                'course_code': 'CSCE 4900',
                'title': 'Database Systems',
                'term_id': '20000000-0000-0000-0000-000000000002',
                'professor_id': '10000000-0000-0000-0000-000000000003',
                'grade': None,
            },
        ],
    )
    op.bulk_insert(
        course_tasks,
        [
            {'id': '40000000-0000-0000-0000-000000000001', 'task_title': 'Requirements Document', 'weight': 20.0, 'course_id': '30000000-0000-0000-0000-000000000001'},
            {'id': '40000000-0000-0000-0000-000000000002', 'task_title': 'Implementation Project', 'weight': 40.0, 'course_id': '30000000-0000-0000-0000-000000000001'},
            {'id': '40000000-0000-0000-0000-000000000003', 'task_title': 'Final Presentation', 'weight': 40.0, 'course_id': '30000000-0000-0000-0000-000000000001'},
            {'id': '40000000-0000-0000-0000-000000000004', 'task_title': 'Midterm Exam', 'weight': 30.0, 'course_id': '30000000-0000-0000-0000-000000000002'},
            {'id': '40000000-0000-0000-0000-000000000005', 'task_title': 'Final Exam', 'weight': 70.0, 'course_id': '30000000-0000-0000-0000-000000000002'},
        ],
    )


def downgrade():
    connection = op.get_bind()
    for table_name, ids in (
        ('course_tasks', [
            '40000000-0000-0000-0000-000000000001',
            '40000000-0000-0000-0000-000000000002',
            '40000000-0000-0000-0000-000000000003',
            '40000000-0000-0000-0000-000000000004',
            '40000000-0000-0000-0000-000000000005',
        ]),
        ('courses', [
            '30000000-0000-0000-0000-000000000001',
            '30000000-0000-0000-0000-000000000002',
            '30000000-0000-0000-0000-000000000003',
        ]),
        ('professors', [
            '10000000-0000-0000-0000-000000000001',
            '10000000-0000-0000-0000-000000000002',
            '10000000-0000-0000-0000-000000000003',
        ]),
        ('terms', [
            '20000000-0000-0000-0000-000000000001',
            '20000000-0000-0000-0000-000000000002',
        ]),
    ):
        table = sa.table(table_name, sa.column('id', sa.Uuid()))
        connection.execute(table.delete().where(table.c.id.in_(ids)))
