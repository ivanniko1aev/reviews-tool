"""add place_id to reviews

Revision ID: 6ffcc02a071e
Revises: bca0d0b33e91
Create Date: 2025-02-14 22:11:29.263071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ffcc02a071e'
down_revision: Union[str, None] = 'bca0d0b33e91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
