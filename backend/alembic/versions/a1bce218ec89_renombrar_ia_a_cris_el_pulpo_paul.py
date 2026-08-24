"""renombrar ia a cris el pulpo paul

Revision ID: a1bce218ec89
Revises: ab7ae044ac33
Create Date: 2026-08-23 20:53:41.867388

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1bce218ec89'
down_revision: Union[str, Sequence[str], None] = 'ab7ae044ac33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade data: renombrar la IA."""
    op.execute(
        "UPDATE users SET username = 'Cris el pulpo Paul', email = 'cris@ipona.ar' "
        "WHERE is_llm"
    )


def downgrade() -> None:
    """Downgrade data."""
    op.execute(
        "UPDATE users SET username = 'ipona-ia', email = 'llm@ipona.ar' WHERE is_llm"
    )
