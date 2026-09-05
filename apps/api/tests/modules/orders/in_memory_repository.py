from dataclasses import replace
from datetime import UTC, datetime

from app.modules.orders.domain.entities import Order, OrderItem


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}
        self._next_order_id = 1
        self._next_item_id = 1

    def add(self, order: Order) -> Order:
        order_id = self._next_order_id
        self._next_order_id += 1
        persisted_items: list[OrderItem] = []

        for item in order.items:
            persisted_items.append(
                replace(item, id=self._next_item_id, order_id=order_id)
            )
            self._next_item_id += 1

        persisted_order = replace(
            order,
            id=order_id,
            created_at=datetime.now(UTC),
            items=tuple(persisted_items),
        )
        self._orders[order_id] = persisted_order
        return persisted_order

    def get_by_id(self, order_id: int) -> Order | None:
        return self._orders.get(order_id)

    def get_by_id_for_update(self, order_id: int) -> Order | None:
        return self.get_by_id(order_id)

    def list_all(self) -> tuple[Order, ...]:
        return tuple(self._orders.values())

    def list_paginated(self, offset: int, limit: int) -> tuple[Order, ...]:
        orders = tuple(self._orders.values())
        return orders[offset : offset + limit]

    def count(self) -> int:
        return len(self._orders)

    def update(self, order: Order) -> Order:
        if order.id is None or order.id not in self._orders:
            raise KeyError(order.id)

        persisted_items: list[OrderItem] = []
        for item in order.items:
            persisted_items.append(
                replace(item, id=self._next_item_id, order_id=order.id)
            )
            self._next_item_id += 1

        persisted_order = replace(order, items=tuple(persisted_items))
        self._orders[order.id] = persisted_order
        return persisted_order

    def delete(self, order: Order) -> None:
        if order.id is None or order.id not in self._orders:
            raise KeyError(order.id)
        del self._orders[order.id]
