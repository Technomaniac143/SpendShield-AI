"""add evidence write permission to procurement managers"""
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "0004_evidence_write_permission"
down_revision = "0003_identity_rbac"
branch_labels = None
depends_on = None


def upgrade():
    permissions = sa.table("permissions", sa.column("id", sa.String), sa.column("name", sa.String))
    roles = sa.table("roles", sa.column("id", sa.String), sa.column("name", sa.String))
    assignments = sa.table(
        "role_permissions",
        sa.column("role_id", sa.String),
        sa.column("permission_id", sa.String),
    )
    connection = op.get_bind()
    permission_id = connection.execute(
        sa.select(permissions.c.id).where(permissions.c.name == "evidence:write")
    ).scalar_one_or_none()
    if permission_id is None:
        permission_id = str(uuid4())
        op.bulk_insert(permissions, [{"id": permission_id, "name": "evidence:write"}])
    procurement_role = connection.execute(
        sa.select(roles.c.id).where(roles.c.name == "PROCUREMENT_MANAGER")
    ).scalar_one()
    exists = connection.execute(sa.select(assignments.c.role_id).where(
        assignments.c.role_id == procurement_role,
        assignments.c.permission_id == permission_id,
    )).scalar_one_or_none()
    if exists is None:
        op.bulk_insert(assignments, [{"role_id": procurement_role, "permission_id": permission_id}])


def downgrade():
    connection = op.get_bind()
    permission_id = connection.execute(
        sa.text("SELECT id FROM permissions WHERE name = 'evidence:write'")
    ).scalar_one_or_none()
    if permission_id is not None:
        connection.execute(sa.text("DELETE FROM role_permissions WHERE permission_id = :permission_id"), {"permission_id": permission_id})
        connection.execute(sa.text("DELETE FROM permissions WHERE id = :permission_id"), {"permission_id": permission_id})