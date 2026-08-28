"""add durable ingestion jobs and row errors"""
from alembic import op
import sqlalchemy as sa

revision = "0006_ingestion"
down_revision = "0005_procurement_foundation"
branch_labels = None
depends_on = None


def upgrade():
    status = sa.Enum("QUEUED", "PROCESSING", "COMPLETED", "PARTIAL", "FAILED", "CANCELLED", name="ingestionstatus")
    op.create_table(
        "ingestion_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_type", sa.String(32), nullable=False),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("status", status, nullable=False),
        sa.Column("source_filename", sa.String(255), nullable=False),
        sa.Column("file_hash", sa.String(64), nullable=False),
        sa.Column("total_rows", sa.Integer, nullable=False, server_default="0"),
        sa.Column("processed_rows", sa.Integer, nullable=False, server_default="0"),
        sa.Column("successful_rows", sa.Integer, nullable=False, server_default="0"),
        sa.Column("failed_rows", sa.Integer, nullable=False, server_default="0"),
        sa.Column("skipped_rows", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column("idempotency_key", sa.String(256)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("last_error", sa.Text),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_ingestion_jobs_tenant_idempotency"),
    )
    op.create_table(
        "ingestion_files",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("job_id", sa.String(36), sa.ForeignKey("ingestion_jobs.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("object_key", sa.String(512), nullable=False),
        sa.Column("content_type", sa.String(128), nullable=False),
        sa.Column("size_bytes", sa.Integer, nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        "ingestion_errors",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("job_id", sa.String(36), sa.ForeignKey("ingestion_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("row_number", sa.Integer, nullable=False),
        sa.Column("field", sa.String(128)),
        sa.Column("error_code", sa.String(64), nullable=False),
        sa.Column("message", sa.String(512), nullable=False),
        sa.Column("raw_value", sa.String(512)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    for table, columns in {
        "ingestion_jobs": ["tenant_id", "entity_type", "status", "file_hash"],
        "ingestion_files": ["tenant_id", "sha256"],
        "ingestion_errors": ["job_id", "tenant_id", "row_number", "error_code"],
    }.items():
        for column in columns:
            op.create_index(f"ix_{table}_{column}", table, [column])


def downgrade():
    for table in ("ingestion_errors", "ingestion_files", "ingestion_jobs"):
        op.drop_table(table)
    sa.Enum(name="ingestionstatus").drop(op.get_bind(), checkfirst=True)