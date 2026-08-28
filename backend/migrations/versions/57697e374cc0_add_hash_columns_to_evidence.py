"""add_hash_columns_to_evidence

Revision ID: 57697e374cc0
"""
from alembic import op
import sqlalchemy as sa

revision = '57697e374cc0'
down_revision = '0007_ingestion_permissions'


def upgrade():
    op.add_column("evidence", sa.Column("previous_hash", sa.String(length=64), nullable=True))
    op.add_column("evidence", sa.Column("record_hash", sa.String(length=64), nullable=True))


def downgrade():
    op.drop_column("evidence", "previous_hash")
    op.drop_column("evidence", "record_hash")
