"""Use INR and decimal transaction amounts

Revision ID: 567d1ca8db1f
Revises: d2813be3ac0b
Create Date: 2026-08-23 10:07:29.077146

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision = "567d1ca8db1f"
down_revision = "d2813be3ac0b"
branch_labels = None
depends_on = None


def upgrade():

    # ----------------------------------------
    # Ensure existing users have INR
    # ----------------------------------------

    op.execute(
        """
        UPDATE users
        SET currency = 'INR'
        WHERE currency IS NULL
           OR currency = ''
        """
    )


    # ----------------------------------------
    # Transactions: FLOAT → NUMERIC(14,2)
    # ----------------------------------------

    with op.batch_alter_table(
        "transactions",
        schema=None
    ) as batch_op:

        batch_op.alter_column(
            "amount",
            existing_type=mysql.FLOAT(),
            type_=sa.Numeric(
                precision=14,
                scale=2
            ),
            existing_nullable=False
        )


    # ----------------------------------------
    # Users: currency → VARCHAR(3) NOT NULL
    # ----------------------------------------

    with op.batch_alter_table(
        "users",
        schema=None
    ) as batch_op:

        batch_op.alter_column(
            "currency",
            existing_type=mysql.VARCHAR(length=10),
            type_=sa.String(length=3),
            nullable=False
        )


def downgrade():

    # ----------------------------------------
    # Users: revert currency constraint/type
    # ----------------------------------------

    with op.batch_alter_table(
        "users",
        schema=None
    ) as batch_op:

        batch_op.alter_column(
            "currency",
            existing_type=sa.String(length=3),
            type_=mysql.VARCHAR(length=10),
            nullable=True
        )


    # ----------------------------------------
    # Transactions: NUMERIC → FLOAT
    # ----------------------------------------

    with op.batch_alter_table(
        "transactions",
        schema=None
    ) as batch_op:

        batch_op.alter_column(
            "amount",
            existing_type=sa.Numeric(
                precision=14,
                scale=2
            ),
            type_=mysql.FLOAT(),
            existing_nullable=False
        )