"""expand audit log events

Revision ID: a8d4c2e7f910
Revises: 3bd26d85b481
Create Date: 2026-09-05
"""

from collections.abc import Sequence

from alembic import op


revision: str = "a8d4c2e7f910"
down_revision: str | Sequence[str] | None = "3bd26d85b481"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_constraint(
        "ck_audit_logs_event_type",
        "audit_logs",
        type_="check",
    )
    op.create_check_constraint(
        "ck_audit_logs_event_type",
        "audit_logs",
        "event_type IN ("
        "'PRODUCT_CREATED', "
        "'PRODUCT_UPDATED', "
        "'PRODUCT_DELETED', "
        "'ORDER_CREATED', "
        "'ORDER_UPDATED', "
        "'ORDER_DELETED', "
        "'STOCK_MOVEMENT'"
        ")",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_audit_logs_event_type",
        "audit_logs",
        type_="check",
    )
    op.create_check_constraint(
        "ck_audit_logs_event_type",
        "audit_logs",
        "event_type IN ("
        "'PRODUCT_CREATED', "
        "'PRODUCT_UPDATED', "
        "'ORDER_CREATED', "
        "'STOCK_MOVEMENT'"
        ")",
    )
