from dataclasses import dataclass
from decimal import Decimal

from app.core.pagination import PageRequest, PageResult
from app.modules.audit_logs.domain.entities import (
    AuditEntityType,
    AuditEventType,
    AuditLog,
)
from app.modules.audit_logs.domain.repositories import AuditLogRepository
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
    def __init__(
        self,
        repository: ProductRepository,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._repository = repository
        self._audit_log_repository = audit_log_repository

    def execute(self, command: CreateProductCommand) -> Product:
        product = Product(
            name=command.name,
            sku=command.sku,
            price=command.price,
            stock_quantity=command.stock_quantity,
        )

        if self._repository.get_by_sku(product.sku) is not None:
            raise ProductSkuAlreadyExistsError(product.sku)

        persisted_product = self._repository.add(product)
        if persisted_product.id is None:
            raise ValueError("A created product must have an ID.")
        self._audit_log_repository.add(
            AuditLog(
                event_type=AuditEventType.PRODUCT_CREATED,
                entity_type=AuditEntityType.PRODUCT,
                entity_id=persisted_product.id,
                details={
                    "name": persisted_product.name,
                    "sku": persisted_product.sku,
                    "price": str(persisted_product.price),
                    "stock_quantity": persisted_product.stock_quantity,
                },
            )
        )
        return persisted_product


class ListProducts:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, page: PageRequest) -> PageResult[Product]:
        products = self._repository.list_paginated(
            offset=page.offset,
            limit=page.page_size,
        )
        return PageResult(
            items=tuple(products),
            page=page.page,
            page_size=page.page_size,
            total_items=self._repository.count(),
        )


class GetProduct:
    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, product_id: int) -> Product:
        product = self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)

        return product


class UpdateProduct:
    def __init__(
        self,
        repository: ProductRepository,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._repository = repository
        self._audit_log_repository = audit_log_repository

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

        persisted_product = self._repository.update(updated_product)
        self._audit_log_repository.add(
            AuditLog(
                event_type=AuditEventType.PRODUCT_UPDATED,
                entity_type=AuditEntityType.PRODUCT,
                entity_id=command.product_id,
                details={
                    "before": self._product_snapshot(current_product),
                    "after": self._product_snapshot(persisted_product),
                },
            )
        )
        if current_product.stock_quantity != persisted_product.stock_quantity:
            self._audit_log_repository.add(
                AuditLog(
                    event_type=AuditEventType.STOCK_MOVEMENT,
                    entity_type=AuditEntityType.PRODUCT,
                    entity_id=command.product_id,
                    details={
                        "reason": AuditEventType.PRODUCT_UPDATED.value,
                        "previous_quantity": current_product.stock_quantity,
                        "change": (
                            persisted_product.stock_quantity
                            - current_product.stock_quantity
                        ),
                        "new_quantity": persisted_product.stock_quantity,
                    },
                )
            )
        return persisted_product

    @staticmethod
    def _product_snapshot(product: Product) -> dict[str, str | int]:
        return {
            "name": product.name,
            "sku": product.sku,
            "price": str(product.price),
            "stock_quantity": product.stock_quantity,
        }


class DeleteProduct:
    def __init__(
        self,
        repository: ProductRepository,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._repository = repository
        self._audit_log_repository = audit_log_repository

    def execute(self, product_id: int) -> None:
        product = self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)

        self._repository.delete(product)
        self._audit_log_repository.add(
            AuditLog(
                event_type=AuditEventType.PRODUCT_DELETED,
                entity_type=AuditEntityType.PRODUCT,
                entity_id=product_id,
                details={
                    "name": product.name,
                    "sku": product.sku,
                    "price": str(product.price),
                    "stock_quantity": product.stock_quantity,
                },
            )
        )


__all__ = [
    "CreateProduct",
    "CreateProductCommand",
    "DeleteProduct",
    "GetProduct",
    "ListProducts",
    "UpdateProduct",
    "UpdateProductCommand",
]
