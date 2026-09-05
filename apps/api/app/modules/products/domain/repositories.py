from collections.abc import Sequence
from typing import Protocol

from app.modules.products.domain.entities import Product


class ProductRepository(Protocol):
    """Persistence contract implemented by the infrastructure layer."""

    def add(self, product: Product) -> Product:
        ...

    def get_by_id(self, product_id: int) -> Product | None:
        ...

    def get_by_sku(self, sku: str) -> Product | None:
        ...

    def get_by_ids_for_update(
        self,
        product_ids: Sequence[int],
    ) -> Sequence[Product]:
        ...

    def list_all(self) -> Sequence[Product]:
        ...

    def list_paginated(self, offset: int, limit: int) -> Sequence[Product]:
        ...

    def count(self) -> int:
        ...

    def update(self, product: Product) -> Product:
        ...

    def delete(self, product: Product) -> None:
        ...


__all__ = ["ProductRepository"]
