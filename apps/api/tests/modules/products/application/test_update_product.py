from decimal import Decimal

import pytest

from app.modules.products.application.errors import (
    ProductNotFoundError,
    ProductSkuAlreadyExistsError,
)
from app.modules.products.application.use_cases import (
    UpdateProduct,
    UpdateProductCommand,
)
from app.modules.products.domain.entities import Product
from app.modules.audit_logs.domain.entities import AuditEventType
from tests.modules.audit_logs.in_memory_repository import InMemoryAuditLogRepository
from tests.modules.products.in_memory_repository import InMemoryProductRepository


def test_update_product() -> None:
    repository = InMemoryProductRepository()
    product = repository.add(
        Product(
            name="Mechanical Keyboard",
            sku="KEY-001",
            price=Decimal("349.90"),
            stock_quantity=10,
        )
    )
    assert product.id is not None
    audit_log_repository = InMemoryAuditLogRepository()

    updated_product = UpdateProduct(repository, audit_log_repository).execute(
        UpdateProductCommand(
            product_id=product.id,
            name="  Mechanical Keyboard Pro  ",
            sku="  key-001  ",
            price=Decimal("449.90"),
            stock_quantity=15,
        )
    )

    assert updated_product.id == product.id
    assert updated_product.created_at == product.created_at
    assert updated_product.name == "Mechanical Keyboard Pro"
    assert updated_product.sku == "KEY-001"
    assert updated_product.price == Decimal("449.90")
    assert updated_product.stock_quantity == 15
    assert repository.get_by_id(product.id) == updated_product
    assert [log.event_type for log in audit_log_repository.list_all()] == [
        AuditEventType.PRODUCT_UPDATED,
        AuditEventType.STOCK_MOVEMENT,
    ]


def test_reject_update_when_product_does_not_exist() -> None:
    repository = InMemoryProductRepository()

    with pytest.raises(ProductNotFoundError, match="999"):
        UpdateProduct(repository, InMemoryAuditLogRepository()).execute(
            UpdateProductCommand(
                product_id=999,
                name="Mechanical Keyboard",
                sku="KEY-001",
                price=Decimal("349.90"),
                stock_quantity=10,
            )
        )


def test_reject_update_with_another_products_sku() -> None:
    repository = InMemoryProductRepository()
    product = repository.add(
        Product(
            name="Mechanical Keyboard",
            sku="KEY-001",
            price=Decimal("349.90"),
            stock_quantity=10,
        )
    )
    other_product = repository.add(
        Product(
            name="Wireless Mouse",
            sku="MOU-001",
            price=Decimal("149.90"),
            stock_quantity=20,
        )
    )
    assert product.id is not None
    audit_log_repository = InMemoryAuditLogRepository()

    with pytest.raises(ProductSkuAlreadyExistsError, match="MOU-001"):
        UpdateProduct(repository, audit_log_repository).execute(
            UpdateProductCommand(
                product_id=product.id,
                name="Mechanical Keyboard",
                sku="  mou-001  ",
                price=Decimal("349.90"),
                stock_quantity=10,
            )
        )

    assert repository.get_by_id(product.id) == product
    assert repository.list_all() == (product, other_product)
    assert audit_log_repository.count() == 0
