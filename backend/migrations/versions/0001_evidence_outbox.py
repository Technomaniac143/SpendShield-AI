"""create evidence and Fabric outbox tables"""
from alembic import op
import sqlalchemy as sa

revision = "0001_evidence_outbox"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "evidence",
        sa.Column("evidence_id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("source_type", sa.String(64), nullable=False),
        sa.Column("source_id", sa.String(128)),
        sa.Column("storage_key", sa.String(512), nullable=False),
        sa.Column("record_id", sa.String(128), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("document_hash", sa.String(64), nullable=False),
        sa.Column("metadata_hash", sa.String(64), nullable=False),
        sa.Column("calculation", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column("event_timestamp", sa.String(64), nullable=False),
        sa.Column("confidence", sa.Float),
        sa.Column("verification_status", sa.String(64), nullable=False),
        sa.Column("fabric_event_id", sa.String(128), nullable=False),
        sa.Column("fabric_transaction_id", sa.String(128)),
        sa.Column("fabric_channel", sa.String(128), nullable=False),
        sa.Column("fabric_chaincode", sa.String(128), nullable=False),
        sa.Column("fabric_block_number", sa.Integer),
        sa.Column("fabric_block_hash", sa.String(128)),
        sa.UniqueConstraint("fabric_event_id", name="uq_evidence_fabric_event"),
    )
    op.create_index("ix_evidence_tenant_id", "evidence", ["tenant_id"])
    op.create_index("ix_evidence_record_id", "evidence", ["record_id"])
    op.create_table(
        "fabric_outbox",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("event_id", sa.String(128), nullable=False),
        sa.Column("event_type", sa.String(64), nullable=False),
        sa.Column("payload", sa.Text, nullable=False),
        sa.Column("status", sa.Enum("PENDING", "PROCESSING", "COMPLETED", "FAILED", name="outboxstatus"), nullable=False),
        sa.Column("attempts", sa.Integer, nullable=False),
        sa.Column("last_error", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index("ix_fabric_outbox_tenant_id", "fabric_outbox", ["tenant_id"])
    op.create_index("ix_fabric_outbox_event_id", "fabric_outbox", ["event_id"])
    op.create_index("ix_fabric_outbox_status", "fabric_outbox", ["status"])


def downgrade():
    op.drop_table("fabric_outbox")
    op.drop_table("evidence")
