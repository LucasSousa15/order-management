from decimal import Decimal

import pytest

from app.modules.orders.domain.entities import (
    Order,
    OrderItem,
    OrderItemSelection,
    OrderValidationError,
)


@pytest.mark.parametrize("quantity", [0, -1])
def test_reject_non_positive_item_quantity(quantity: int) -> None:
    with pytest.raises(OrderValidationError, match="quantity"):
        OrderItemSelection(product_id=1, quantity=quantity)


def test_reject_empty_order() -> None:
    with pytest.raises(OrderValidationError, match="at least one"):
        Order(items=())


def test_reject_duplicate_products_in_order() -> None:
    item = OrderItem(
        product_id=1,
        quantity=1,
        unit_price=Decimal("10.00"),
    )

    with pytest.raises(OrderValidationError, match="only once"):
        Order(items=(item, item))
