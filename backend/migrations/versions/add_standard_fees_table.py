"""Add standard_fees table

Revision ID: 3a7b9c2d4e5f
Revises: previous_revision_id
Create Date: 2025-05-16 10:52:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a7b9c2d4e5f'
down_revision = None  # Update this with the actual previous revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Create standard_fees table
    op.create_table(
        'standard_fees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('course_id', sa.Integer(), nullable=False),
        sa.Column('semester_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
        sa.ForeignKeyConstraint(['semester_id'], ['semesters.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('course_id', 'semester_id', name='uix_standard_fee_course_semester')
    )
    op.create_index(op.f('ix_standard_fees_id'), 'standard_fees', ['id'], unique=False)
    
    # Modify student_fees table to make amount nullable
    op.alter_column('student_fees', 'amount',
               existing_type=sa.Float(),
               nullable=True)


def downgrade():
    # Revert student_fees.amount to non-nullable
    op.alter_column('student_fees', 'amount',
               existing_type=sa.Float(),
               nullable=False)
    
    # Drop standard_fees table
    op.drop_index(op.f('ix_standard_fees_id'), table_name='standard_fees')
    op.drop_table('standard_fees')
