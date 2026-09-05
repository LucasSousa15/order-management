from decimal import Decimal

import pytest

from app.modules.orders.application.errors import (
    InsufficientStockError,
    OrderProductNotFoundError,
)
from app.modules.orders.application.use_cases import CreateOrder, CreateOrderCommand
from app.modules.orders.domain.entities import OrderItemSelection
from app.modules.audit_logs.domain.entities import AuditEventType
from app.modules.products.domain.entities import Product
from tests.modules.audit_logs.in_memory_repository import InMemoryAuditLogRepository
from tests.modules.orders.in_memory_repository import InMemoryOrderRepository
from tests.modules.products.in_memory_repository import InMemoryProductRepository


def add_product(
    repository: InMemoryProductRepository,
    *,
    sku: str,
    price: str,
    stock_quantity: int,
) -> Product:
    return repository.add(
        Product(
            name=f"Product {sku}",
            sku=sku,
            price=Decimal(price),
            stock_quantity=stock_quantity,
        )
    )


def test_create_order_with_one_product_and_decrement_stock() -> None:
    product_repository = InMemoryProductRepository()
    order_repository = InMemoryOrderRepository()
    audit_log_repository = InMemoryAuditLogRepository()
    product = add_product(
        product_repository,
        sku="PRO-001",
        price="25.90",
        stock_quantity=3,
    )
    assert product.id is not None

    order = CreateOrder(
        order_repository,
        product_repository,
        audit_log_repository,
    ).execute(
        CreateOrderCommand(
            items=(OrderItemSelection(product_id=product.id, quantity=1),)
        )
    )

    assert order.id == 1
    assert order.created_at is not None
    assert len(order.items) == 1
    assert order.items[0].product_id == product.id
    assert order.items[0].quantity == 1
    assert order.items[0].unit_price == Decimal("25.90")
    assert order_repository.get_by_id(order.id) == order
    assert product_repository.require_by_id(product.id).stock_quantity == 2
    assert [log.event_type for log in audit_log_repository.list_all()] == [
        AuditEventType.STOCK_MOVEMENT,
        AuditEventType.ORDER_CREATED,
    ]


def test_create_order_with_multiple_products() -> None:
    product_repository = InMemoryProductRepository()
    order_repository = InMemoryOrderRepository()
    first_product = add_product(
        product_repository,
        sku="PRO-001",
        price="25.90",
        stock_quantity=5,
    )
    second_product = add_product(
        product_repository,
        sku="PRO-002",
        price="10.50",
        stock_quantity=4,
    )
    assert first_product.id is not None
    assert second_product.id is not None

    order = CreateOrder(
        order_repository,
        product_repository,
        InMemoryAuditLogRepository(),
    ).execute(
        CreateOrderCommand(
            items=(
                OrderItemSelection(product_id=first_product.id, quantity=2),
                OrderItemSelection(product_id=second_product.id, quantity=3),
            )
        )
    )

    assert len(order.items) == 2
    assert product_repository.require_by_id(first_product.id).stock_quantity == 3
    assert product_repository.require_by_id(second_product.id).stock_quantity == 1


def test_reject_order_with_missing_product() -> None:
    product_repository = InMemoryProductRepository()
    order_repository = InMemoryOrderRepository()

    with pytest.raises(OrderProductNotFoundError, match="999"):
        CreateOrder(
            order_repository,
            product_repository,
            InMemoryAuditLogRepository(),
        ).execute(
            CreateOrderCommand(
                items=(OrderItemSelection(product_id=999, quantity=1),)
            )
        )

    assert order_repository.list_all() == ()


@pytest.mark.parametrize(
    ("stock_quantity", "requested_quantity"),
    [(0, 1), (1, 2)],
)
def test_reject_order_with_insufficient_stock(
    stock_quantity: int,
    requested_quantity: int,
) -> None:
    product_repository = InMemoryProductRepository()
    order_repository = InMemoryOrderRepository()
    product = add_product(
        product_repository,
        sku="PRO-001",
        price="25.90",
        stock_quantity=stock_quantity,
    )
    assert product.id is not None

    with pytest.raises(InsufficientStockError, match=str(product.id)):
        CreateOrder(
            order_repository,
            product_repository,
            InMemoryAuditLogRepository(),
        ).execute(
            CreateOrderCommand(
                items=(
                    OrderItemSelection(
                        product_id=product.id,
                        quantity=requested_quantity,
                    ),
                )
            )
        )

    assert product_repository.get_by_id(product.id) == product
    assert order_repository.list_all() == ()


def test_validate_every_stock_before_changing_any_product() -> None:
    product_repository = InMemoryProductRepository()
    order_repository = InMemoryOrderRepository()
    available_product = add_product(
        product_repository,
        sku="PRO-001",
        price="25.90",
        stock_quantity=5,
    )
    unavailable_product = add_product(
        product_repository,
        sku="PRO-002",
        price="10.50",
        stock_quantity=0,
    )
    assert available_product.id is not None
    assert unavailable_product.id is not None

    with pytest.raises(InsufficientStockError):
        CreateOrder(
            order_repository,
            product_repository,
            InMemoryAuditLogRepository(),
        ).execute(
            CreateOrderCommand(
                items=(
                    OrderItemSelection(
                        product_id=available_product.id,
                        quantity=2,
                    ),
                    OrderItemSelection(
                        product_id=unavailable_product.id,
                        quantity=1,
                    ),
                )
            )
        )

    assert product_repository.get_by_id(available_product.id) == available_product
    assert product_repository.get_by_id(unavailable_product.id) == unavailable_product
    assert order_repository.list_all() == ()
