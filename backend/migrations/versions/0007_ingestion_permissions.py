"""add ingestion permissions"""
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "0007_ingestion_permissions"
down_revision = "0006_ingestion"
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    permissions = sa.table("permissions", sa.column("id", sa.String), sa.column("name", sa.String))
    roles = sa.table("roles", sa.column("id", sa.String), sa.column("name", sa.String))
    assignments = sa.table("role_permissions", sa.column("role_id", sa.String), sa.column("permission_id", sa.String))
    names = {"ingestion:read", "ingestion:write", "ingestion:cancel"}
    ids = {}
    for name in names:
        permission_id = connection.execute(sa.select(permissions.c.id).where(permissions.c.name == name)).scalar_one_or_none()
        if permission_id is None:
            permission_id = str(uuid4())
            op.bulk_insert(permissions, [{"id": permission_id, "name": name}])
        ids[name] = permission_id
    role_ids = dict(connection.execute(sa.select(roles.c.name, roles.c.id)).all())
    for role_name in ("ADMIN", "PROCUREMENT_MANAGER"):
        role_id = role_ids[role_name]
        for permission_id in ids.values():
            exists = connection.execute(sa.select(assignments.c.role_id).where(assignments.c.role_id == role_id, assignments.c.permission_id == permission_id)).scalar_one_or_none()
            if exists is None:
                op.bulk_insert(assignments, [{"role_id": role_id, "permission_id": permission_id}])


def downgrade():
    connection = op.get_bind()
    permission_ids = [row[0] for row in connection.execute(sa.text("SELECT id FROM permissions WHERE name LIKE 'ingestion:%'")).all()]
    if permission_ids:
        connection.execute(sa.text("DELETE FROM role_permissions WHERE permission_id IN (SELECT id FROM permissions WHERE name LIKE 'ingestion:%')"))
        connection.execute(sa.text("DELETE FROM permissions WHERE name LIKE 'ingestion:%'"))