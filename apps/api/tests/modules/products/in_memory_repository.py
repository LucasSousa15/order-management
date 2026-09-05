from collections.abc import Sequence
from dataclasses import replace
from datetime import UTC, datetime

from app.modules.products.domain.entities import Product


class InMemoryProductRepository:
    def __init__(self) -> None:
        self._products: dict[int, Product] = {}
        self._next_id = 1

    def add(self, product: Product) -> Product:
        persisted_product = replace(
            product,
            id=self._next_id,
            created_at=datetime.now(UTC),
        )
        self._products[self._next_id] = persisted_product
        self._next_id += 1
        return persisted_product

    def get_by_id(self, product_id: int) -> Product | None:
        return self._products.get(product_id)

    def get_by_sku(self, sku: str) -> Product | None:
        normalized_sku = sku.strip().upper()
        return next(
            (
                product
                for product in self._products.values()
                if product.sku == normalized_sku
            ),
            None,
        )

    def get_by_ids_for_update(
        self,
        product_ids: Sequence[int],
    ) -> tuple[Product, ...]:
        return tuple(
            product
            for product_id in product_ids
            if (product := self._products.get(product_id)) is not None
        )

    def list_all(self) -> tuple[Product, ...]:
        return tuple(self._products.values())

    def list_paginated(self, offset: int, limit: int) -> tuple[Product, ...]:
        products = tuple(self._products.values())
        return products[offset : offset + limit]

    def count(self) -> int:
        return len(self._products)

    def update(self, product: Product) -> Product:
        if product.id is None or product.id not in self._products:
            raise KeyError(product.id)
        self._products[product.id] = product
        return product

    def delete(self, product: Product) -> None:
        if product.id is None or product.id not in self._products:
            raise KeyError(product.id)
        del self._products[product.id]
