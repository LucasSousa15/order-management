from decimal import Decimal

import pytest

from app.modules.orders.application.errors import (
    InsufficientStockError,
    OrderNotFoundError,
)
from app.modules.orders.application.use_cases import (
    CreateOrder,
    CreateOrderCommand,
    DeleteOrder,
    GetOrder,
    UpdateOrder,
    UpdateOrderCommand,
)
from app.modules.orders.domain.entities import Order, OrderItemSelection
from app.modules.products.domain.entities import Product
from tests.modules.orders.in_memory_repository import InMemoryOrderRepository
from tests.modules.products.in_memory_repository import InMemoryProductRepository


def add_product(
    repository: InMemoryProductRepository,
    *,
    sku: str,
    stock_quantity: int,
) -> Product:
    return repository.add(
        Product(
            name=f"Product {sku}",
            sku=sku,
            price=Decimal("25.90"),
            stock_quantity=stock_quantity,
        )
    )


def create_order(
    order_repository: InMemoryOrderRepository,
    product_repository: InMemoryProductRepository,
    product: Product,
    quantity: int,
) -> Order:
    assert product.id is not None
    return CreateOrder(order_repository, product_repository).execute(
        CreateOrderCommand(
            items=(
                OrderItemSelection(
                    product_id=product.id,
                    quantity=quantity,
                ),
            )
        )
    )


def test_get_order_by_id() -> None:
    order_repository = InMemoryOrderRepository()
    product_repository = InMemoryProductRepository()
    product = add_product(
        product_repository,
        sku="PRO-001",
        stock_quantity=5,
    )
    order = create_order(order_repository, product_repository, product, 2)
    assert order.id is not None

    assert GetOrder(order_repository).execute(order.id) == order


def test_reject_get_when_order_does_not_exist() -> None:
    with pytest.raises(OrderNotFoundError, match="999"):
        GetOrder(InMemoryOrderRepository()).execute(999)


def test_update_order_reconciles_product_stocks() -> None:
    order_repository = InMemoryOrderRepository()
    product_repository = InMemoryProductRepository()
    first_product = add_product(
        product_repository,
        sku="PRO-001",
        stock_quantity=5,
    )
    second_product = add_product(
        product_repository,
        sku="PRO-002",
        stock_quantity=4,
    )
    order = create_order(order_repository, product_repository, first_product, 2)
    assert order.id is not None
    assert first_product.id is not None
    assert second_product.id is not None

    updated_order = UpdateOrder(order_repository, product_repository).execute(
        UpdateOrderCommand(
            order_id=order.id,
            items=(
                OrderItemSelection(product_id=first_product.id, quantity=1),
                OrderItemSelection(product_id=second_product.id, quantity=3),
            ),
        )
    )

    assert updated_order.id == order.id
    assert updated_order.created_at == order.created_at
    assert [(item.product_id, item.quantity) for item in updated_order.items] == [
        (first_product.id, 1),
        (second_product.id, 3),
    ]
    assert product_repository.get_by_id(first_product.id).stock_quantity == 4  # type: ignore[union-attr]
    assert product_repository.get_by_id(second_product.id).stock_quantity == 1  # type: ignore[union-attr]


def test_reject_update_when_order_does_not_exist() -> None:
    with pytest.raises(OrderNotFoundError, match="999"):
        UpdateOrder(
            InMemoryOrderRepository(),
            InMemoryProductRepository(),
        ).execute(
            UpdateOrderCommand(
                order_id=999,
                items=(OrderItemSelection(product_id=1, quantity=1),),
            )
        )


def test_reject_order_update_without_changing_order_or_stock() -> None:
    order_repository = InMemoryOrderRepository()
    product_repository = InMemoryProductRepository()
    product = add_product(
        product_repository,
        sku="PRO-001",
        stock_quantity=2,
    )
    order = create_order(order_repository, product_repository, product, 2)
    assert order.id is not None
    assert product.id is not None

    with pytest.raises(InsufficientStockError, match="Insufficient stock"):
        UpdateOrder(order_repository, product_repository).execute(
            UpdateOrderCommand(
                order_id=order.id,
                items=(OrderItemSelection(product_id=product.id, quantity=3),),
            )
        )

    assert order_repository.get_by_id(order.id) == order
    assert product_repository.get_by_id(product.id).stock_quantity == 0  # type: ignore[union-attr]


def test_delete_order_restores_stock() -> None:
    order_repository = InMemoryOrderRepository()
    product_repository = InMemoryProductRepository()
    product = add_product(
        product_repository,
        sku="PRO-001",
        stock_quantity=5,
    )
    order = create_order(order_repository, product_repository, product, 2)
    assert order.id is not None
    assert product.id is not None

    result = DeleteOrder(order_repository, product_repository).execute(order.id)

    assert result is None
    assert order_repository.get_by_id(order.id) is None
    assert product_repository.get_by_id(product.id).stock_quantity == 5  # type: ignore[union-attr]


def test_reject_delete_when_order_does_not_exist() -> None:
    with pytest.raises(OrderNotFoundError, match="999"):
        DeleteOrder(
            InMemoryOrderRepository(),
            InMemoryProductRepository(),
        ).execute(999)
