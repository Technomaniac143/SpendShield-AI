"""add tenants, users, roles, permissions, and refresh sessions"""
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "0003_identity_rbac"
down_revision = "0002_outbox_leases"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(64), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
    )
    op.create_table(
        "permissions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("display_name", sa.String(128), nullable=False),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", sa.String(36), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.String(36), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("permission_id", sa.String(36), sa.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "refresh_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", sa.String(36), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("family_id", sa.String(36), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("replaced_by_hash", sa.String(64)),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_active", "users", ["active"])
    op.create_index("ix_refresh_sessions_user_id", "refresh_sessions", ["user_id"])
    op.create_index("ix_refresh_sessions_tenant_id", "refresh_sessions", ["tenant_id"])
    op.create_index("ix_refresh_sessions_family_id", "refresh_sessions", ["family_id"])
    op.create_index("ix_refresh_sessions_expires_at", "refresh_sessions", ["expires_at"])

    roles = {name: str(uuid4()) for name in ["ADMIN", "CFO", "PROCUREMENT_MANAGER", "FINANCE", "AUDITOR", "VIEWER"]}
    permission_names = [
        "supplier:read", "supplier:write", "invoice:read", "invoice:write",
        "investigation:read", "investigation:create", "recommendation:read",
        "recommendation:decide", "evidence:read", "evidence:write", "evidence:verify", "outcome:write", "admin:users",
    ]
    permissions = {name: str(uuid4()) for name in permission_names}
    op.bulk_insert(sa.table("roles", sa.column("id"), sa.column("name")), [{"id": value, "name": key} for key, value in roles.items()])
    op.bulk_insert(sa.table("permissions", sa.column("id"), sa.column("name")), [{"id": value, "name": key} for key, value in permissions.items()])
    read_permissions = {name for name in permission_names if name.endswith(":read") or name == "evidence:verify"}
    role_permissions_map = {
        "ADMIN": set(permission_names),
        "CFO": {"invoice:read", "investigation:read", "recommendation:read", "recommendation:decide", "evidence:read", "evidence:verify", "outcome:write"},
        "PROCUREMENT_MANAGER": {"supplier:read", "supplier:write", "invoice:read", "invoice:write", "investigation:read", "investigation:create", "recommendation:read", "evidence:read", "evidence:write", "evidence:verify"},
        "FINANCE": {"invoice:read", "invoice:write", "investigation:read", "recommendation:read", "evidence:read", "evidence:verify", "outcome:write"},
        "AUDITOR": read_permissions | {"investigation:read", "investigation:create", "recommendation:read", "evidence:read"},
        "VIEWER": read_permissions | {"investigation:read", "recommendation:read", "evidence:read"},
    }
    assignments = [
        {"role_id": roles[role_name], "permission_id": permissions[permission_name]}
        for role_name, permission_set in role_permissions_map.items()
        for permission_name in permission_set
    ]
    op.bulk_insert(sa.table("role_permissions", sa.column("role_id"), sa.column("permission_id")), assignments)


def downgrade():
    op.drop_table("refresh_sessions")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("tenants")