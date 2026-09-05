from collections.abc import Sequence
from typing import Protocol

from app.modules.orders.domain.entities import Order


class OrderRepository(Protocol):
    def add(self, order: Order) -> Order:
        ...

    def get_by_id(self, order_id: int) -> Order | None:
        ...

    def get_by_id_for_update(self, order_id: int) -> Order | None:
        ...

    def list_all(self) -> Sequence[Order]:
        ...

    def list_paginated(self, offset: int, limit: int) -> Sequence[Order]:
        ...

    def count(self) -> int:
        ...

    def update(self, order: Order) -> Order:
        ...

    def delete(self, order: Order) -> None:
        ...


__all__ = ["OrderRepository"]
