from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.core.http.pagination import PaginationMetaViewModel
from app.core.pagination import PageResult
from app.modules.orders.domain.entities import Order, OrderItem


class OrderItemViewModel(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal

    @classmethod
    def from_entity(cls, item: OrderItem) -> "OrderItemViewModel":
        if item.id is None:
            raise ValueError("Only persisted order items can be exposed by the API.")
        return cls(
            id=item.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
        )


class OrderViewModel(BaseModel):
    id: int
    created_at: datetime
    items: list[OrderItemViewModel]

    @classmethod
    def from_entity(cls, order: Order) -> "OrderViewModel":
        if order.id is None or order.created_at is None:
            raise ValueError("Only persisted orders can be exposed by the API.")
        return cls(
            id=order.id,
            created_at=order.created_at,
            items=[OrderItemViewModel.from_entity(item) for item in order.items],
        )


class OrderListViewModel(BaseModel):
    data: list[OrderViewModel]
    meta: PaginationMetaViewModel

    @classmethod
    def from_page(cls, page: PageResult[Order]) -> "OrderListViewModel":
        return cls(
            data=[OrderViewModel.from_entity(order) for order in page.items],
            meta=PaginationMetaViewModel.from_page(page),
        )


__all__ = ["OrderItemViewModel", "OrderListViewModel", "OrderViewModel"]
