"""Link policies to virtual accounts

Revision ID: 3c4d5e6f7g8h
Revises: a1b2c3d4e5f6
Create Date: 2025-10-22 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c4d5e6f7g8h'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('virtual_accounts', sa.Column('policy_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_virtual_accounts_policy_id'), 'virtual_accounts', ['policy_id'], unique=False)
    op.create_foreign_key('fk_virtual_accounts_policy_id', 'virtual_accounts', 'policies', ['policy_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_virtual_accounts_policy_id', 'virtual_accounts', type_='foreignkey')
    op.drop_index(op.f('ix_virtual_accounts_policy_id'), table_name='virtual_accounts')
    op.drop_column('virtual_accounts', 'policy_id')
