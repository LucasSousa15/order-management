"""create initial schema

Revision ID: 3bd26d85b481
Revises: 
Create Date: 2026-09-05 19:33:24.159621
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = '3bd26d85b481'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table('audit_logs',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.Column('entity_type', sa.String(length=30), nullable=False),
    sa.Column('entity_id', sa.BigInteger(), nullable=False),
    sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint("entity_type IN ('PRODUCT', 'ORDER')", name='ck_audit_logs_entity_type'),
    sa.CheckConstraint("event_type IN ('PRODUCT_CREATED', 'PRODUCT_UPDATED', 'ORDER_CREATED', 'STOCK_MOVEMENT')", name='ck_audit_logs_event_type'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'], unique=False)
    op.create_index('ix_audit_logs_entity', 'audit_logs', ['entity_type', 'entity_id'], unique=False)
    op.create_table('orders',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('sku', sa.String(length=64), nullable=False),
    sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('stock_quantity', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('length(trim(name)) > 0', name='ck_products_name_not_blank'),
    sa.CheckConstraint('length(trim(sku)) > 0', name='ck_products_sku_not_blank'),
    sa.CheckConstraint('price > 0', name='ck_products_price_positive'),
    sa.CheckConstraint('stock_quantity >= 0', name='ck_products_stock_non_negative'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=True)
    op.create_table('order_items',
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('order_id', sa.BigInteger(), nullable=False),
    sa.Column('product_id', sa.BigInteger(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.CheckConstraint('quantity > 0', name='ck_order_items_quantity_positive'),
    sa.CheckConstraint('unit_price > 0', name='ck_order_items_unit_price_positive'),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_id', 'product_id', name='uq_order_items_order_product')
    )
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_order_items_product_id'), table_name='order_items')
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items')
    op.drop_table('order_items')
    op.drop_index(op.f('ix_products_sku'), table_name='products')
    op.drop_table('products')
    op.drop_table('orders')
    op.drop_index('ix_audit_logs_entity', table_name='audit_logs')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_table('audit_logs')
