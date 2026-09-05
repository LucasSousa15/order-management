from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


class OrderValidationError(ValueError):
    pass


def _validate_product_id(product_id: int) -> None:
    if (
        not isinstance(product_id, int)
        or isinstance(product_id, bool)
        or product_id <= 0
    ):
        raise OrderValidationError("Order item product ID must be a positive integer.")


def _validate_quantity(quantity: int) -> None:
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        raise OrderValidationError("Order item quantity must be a positive integer.")


@dataclass(frozen=True, slots=True)
class OrderItemSelection:
    product_id: int
    quantity: int

    def __post_init__(self) -> None:
        _validate_product_id(self.product_id)
        _validate_quantity(self.quantity)


@dataclass(frozen=True, slots=True)
class OrderItem:
    product_id: int
    quantity: int
    unit_price: Decimal
    id: int | None = None
    order_id: int | None = None

    def __post_init__(self) -> None:
        _validate_product_id(self.product_id)
        _validate_quantity(self.quantity)
        if (
            not isinstance(self.unit_price, Decimal)
            or not self.unit_price.is_finite()
            or self.unit_price <= Decimal("0")
        ):
            raise OrderValidationError("Order item unit price must be positive.")


@dataclass(frozen=True, slots=True)
class Order:
    items: tuple[OrderItem, ...]
    id: int | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.items:
            raise OrderValidationError("An order must contain at least one item.")

        product_ids = [item.product_id for item in self.items]
        if len(product_ids) != len(set(product_ids)):
            raise OrderValidationError(
                "Each product can appear only once in an order."
            )


__all__ = [
    "Order",
    "OrderItem",
    "OrderItemSelection",
    "OrderValidationError",
]
