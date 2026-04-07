"""Frontend schema extensions: image_url, maintenance timestamps."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260405_0002"
down_revision = "20260404_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "sensor_groups",
        sa.Column("image_url", sa.Text(), nullable=True),
    )

    op.add_column(
        "equipment",
        sa.Column("maintenance_due_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "equipment",
        sa.Column("maintenance_completed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("equipment", "maintenance_completed_at")
    op.drop_column("equipment", "maintenance_due_at")
    op.drop_column("sensor_groups", "image_url")
