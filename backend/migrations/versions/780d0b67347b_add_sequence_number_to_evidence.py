"""add_sequence_number_to_evidence

Revision ID: 780d0b67347b
"""
from alembic import op
import sqlalchemy as sa

revision = '780d0b67347b'
down_revision = 'a5ef76fb82ab'


def upgrade():
    op.add_column('evidence', sa.Column('sequence_number', sa.Integer(), autoincrement=True, nullable=True))
    
    # Populate existing rows sequentially
    connection = op.get_bind()
    metadata = sa.MetaData()
    # We construct a Table definition to run updates
    evidence_table = sa.Table(
        'evidence', 
        metadata,
        sa.Column('evidence_id', sa.String(36), primary_key=True),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('sequence_number', sa.Integer())
    )
    
    # Fetch all records sorted by created_at, then evidence_id
    rows = connection.execute(
        sa.select(evidence_table.c.evidence_id).order_by(evidence_table.c.created_at.asc(), evidence_table.c.evidence_id.asc())
    ).all()
    
    for idx, row in enumerate(rows, start=1):
        connection.execute(
            evidence_table.update().where(evidence_table.c.evidence_id == row[0]).values(sequence_number=idx)
        )


def downgrade():
    op.drop_column('evidence', 'sequence_number')
