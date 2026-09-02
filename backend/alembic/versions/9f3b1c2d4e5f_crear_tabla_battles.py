"""crear tabla battles

Revision ID: 9f3b1c2d4e5f
Revises: a1bce218ec89
Create Date: 2026-09-02 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9f3b1c2d4e5f'
down_revision: Union[str, Sequence[str], None] = 'a1bce218ec89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Crear tabla battles para las batallas diarias."""
    op.create_table(
        "battles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("battle_date", sa.Date(), nullable=False),
        sa.Column("user_a_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("user_b_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("extra_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("status", sa.String(20), server_default="pendiente", nullable=False),
        sa.Column("winner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("message", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("idx_battles_date", "battles", ["battle_date"])
    op.create_index("idx_battles_users", "battles", ["user_a_id", "user_b_id", "extra_user_id"])


def downgrade() -> None:
    """Eliminar tabla battles."""
    op.drop_index("idx_battles_users", table_name="battles")
    op.drop_index("idx_battles_date", table_name="battles")
    op.drop_table("battles")
