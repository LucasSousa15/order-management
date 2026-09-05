from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal

from app.modules.products.application.errors import (
    ProductNotFoundError,
    ProductSkuAlreadyExistsError,
)
from app.modules.products.domain.entities import Product
from app.modules.products.domain.repositories import ProductRepository


@dataclass(frozen=True, slots=True)
class CreateProductCommand:
    name: str
    sku: str
    price: Decimal
    stock_quantity: int


@dataclass(frozen=True, slots=True)
class UpdateProductCommand:
    product_id: int
    name: str
    sku: str
    price: Decimal
    stock_quantity: int


class CreateProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, command: CreateProductCommand) -> Product:
        product = Product(
            name=command.name,
            sku=command.sku,
            price=command.price,
            stock_quantity=command.stock_quantity,
        )

        if self._repository.get_by_sku(product.sku) is not None:
            raise ProductSkuAlreadyExistsError(product.sku)

        return self._repository.add(product)


class ListProducts:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self) -> Sequence[Product]:
        return self._repository.list_all()


class GetProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, product_id: int) -> Product:
        product = self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)

        return product


class UpdateProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, command: UpdateProductCommand) -> Product:
        current_product = self._repository.get_by_id(command.product_id)
        if current_product is None:
            raise ProductNotFoundError(command.product_id)

        updated_product = Product(
            id=command.product_id,
            name=command.name,
            sku=command.sku,
            price=command.price,
            stock_quantity=command.stock_quantity,
            created_at=current_product.created_at,
        )

        product_with_sku = self._repository.get_by_sku(updated_product.sku)
        if (
            product_with_sku is not None
            and product_with_sku.id != current_product.id
        ):
            raise ProductSkuAlreadyExistsError(updated_product.sku)

        return self._repository.update(updated_product)


class DeleteProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, product_id: int) -> None:
        product = self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)

        self._repository.delete(product)


__all__ = [
    "CreateProduct",
    "CreateProductCommand",
    "DeleteProduct",
    "GetProduct",
    "ListProducts",
    "UpdateProduct",
    "UpdateProductCommand",
]
