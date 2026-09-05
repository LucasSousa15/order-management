from decimal import Decimal
from uuid import uuid4

from app.core.database.service import database
from app.modules.audit_logs.infra.database.repository import SqlAlchemyAuditLogRepository
from app.modules.audit_logs.domain.entities import AuditEventType
from app.modules.orders.application.use_cases import (
    CreateOrder,
    CreateOrderCommand,
    DeleteOrder,
    UpdateOrder,
    UpdateOrderCommand,
)
from app.modules.orders.domain.entities import OrderItemSelection
from app.modules.orders.infra.database.repository import SqlAlchemyOrderRepository
from app.modules.products.domain.entities import Product
from app.modules.products.infra.database.repository import (
    SqlAlchemyProductRepository,
)


def test_create_order_updates_product_stock_in_database() -> None:
    session = database.session()
    product_repository = SqlAlchemyProductRepository(session)
    order_repository = SqlAlchemyOrderRepository(session)
    audit_log_repository = SqlAlchemyAuditLogRepository(session)

    try:
        product = product_repository.add(
            Product(
                name="Order stock integration test",
                sku=f"ORDER-STOCK-{uuid4().hex[:12].upper()}",
                price=Decimal("25.90"),
                stock_quantity=3,
            )
        )
        assert product.id is not None

        order = CreateOrder(
            order_repository,
            product_repository,
            audit_log_repository,
        ).execute(
            CreateOrderCommand(
                items=(OrderItemSelection(product_id=product.id, quantity=2),)
            )
        )
        assert order.id is not None
        order_id = order.id
        session.expire_all()

        persisted_product = product_repository.get_by_id(product.id)
        persisted_order = order_repository.get_by_id(order_id)
        assert persisted_product is not None
        assert persisted_product.stock_quantity == 1
        assert persisted_order == order

        updated_order = UpdateOrder(
            order_repository,
            product_repository,
            audit_log_repository,
        ).execute(
            UpdateOrderCommand(
                order_id=order_id,
                items=(OrderItemSelection(product_id=product.id, quantity=1),),
            )
        )
        session.expire_all()
        product_after_update = product_repository.get_by_id(product.id)
        assert product_after_update is not None
        assert product_after_update.stock_quantity == 2
        assert updated_order.items[0].quantity == 1

        DeleteOrder(
            order_repository,
            product_repository,
            audit_log_repository,
        ).execute(order_id)
        session.expire_all()
        product_after_delete = product_repository.get_by_id(product.id)
        assert product_after_delete is not None
        assert product_after_delete.stock_quantity == 3
        assert order_repository.get_by_id(order_id) is None
        assert [
            audit_log.event_type
            for audit_log in reversed(
                audit_log_repository.list_paginated(offset=0, limit=6)
            )
        ] == [
            AuditEventType.STOCK_MOVEMENT,
            AuditEventType.ORDER_CREATED,
            AuditEventType.STOCK_MOVEMENT,
            AuditEventType.ORDER_UPDATED,
            AuditEventType.STOCK_MOVEMENT,
            AuditEventType.ORDER_DELETED,
        ]
    finally:
        session.rollback()
        session.close()
