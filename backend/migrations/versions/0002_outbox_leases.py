"""add outbox lease and retry scheduling fields"""
from alembic import op
import sqlalchemy as sa

revision = "0002_outbox_leases"
down_revision = "0001_evidence_outbox"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("fabric_outbox", sa.Column("locked_at", sa.DateTime(timezone=True)))
    op.add_column("fabric_outbox", sa.Column("locked_by", sa.String(128)))
    op.add_column("fabric_outbox", sa.Column("next_attempt_at", sa.DateTime(timezone=True)))
    op.create_index("ix_fabric_outbox_retry", "fabric_outbox", ["status", "next_attempt_at", "created_at"])


def downgrade():
    op.drop_index("ix_fabric_outbox_retry", table_name="fabric_outbox")
    op.drop_column("fabric_outbox", "next_attempt_at")
    op.drop_column("fabric_outbox", "locked_by")
    op.drop_column("fabric_outbox", "locked_at")