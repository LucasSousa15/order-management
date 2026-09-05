from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.service import Base


class ProductModel(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_products_name_not_blank",
        ),
        CheckConstraint(
            "length(trim(sku)) > 0",
            name="ck_products_sku_not_blank",
        ),
        CheckConstraint("price > 0", name="ck_products_price_positive"),
        CheckConstraint(
            "stock_quantity >= 0",
            name="ck_products_stock_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    sku: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    order_items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="product",
        passive_deletes=True,
    )


class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    items: Mapped[list["OrderItemModel"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class OrderItemModel(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="ck_order_items_quantity_positive",
        ),
        CheckConstraint(
            "unit_price > 0",
            name="ck_order_items_unit_price_positive",
        ),
        UniqueConstraint(
            "order_id",
            "product_id",
            name="uq_order_items_order_product",
        ),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    order: Mapped[OrderModel] = relationship(back_populates="items")
    product: Mapped[ProductModel] = relationship(back_populates="order_items")


class AuditLogModel(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        CheckConstraint(
            "event_type IN ("
            "'PRODUCT_CREATED', "
            "'PRODUCT_UPDATED', "
            "'ORDER_CREATED', "
            "'STOCK_MOVEMENT'"
            ")",
            name="ck_audit_logs_event_type",
        ),
        CheckConstraint(
            "entity_type IN ('PRODUCT', 'ORDER')",
            name="ck_audit_logs_entity_type",
        ),
        Index(
            "ix_audit_logs_entity",
            "entity_type",
            "entity_id",
        ),
        Index("ix_audit_logs_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(30), nullable=False)
    entity_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    details: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


__all__ = [
    "AuditLogModel",
    "OrderItemModel",
    "OrderModel",
    "ProductModel",
]
