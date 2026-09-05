from decimal import Decimal

import pytest

from app.modules.products.application.errors import ProductSkuAlreadyExistsError
from app.modules.products.application.use_cases import (
    CreateProduct,
    CreateProductCommand,
)
from app.modules.audit_logs.domain.entities import AuditEventType
from tests.modules.audit_logs.in_memory_repository import InMemoryAuditLogRepository
from tests.modules.products.in_memory_repository import InMemoryProductRepository


def test_create_product() -> None:
    repository = InMemoryProductRepository()
    audit_log_repository = InMemoryAuditLogRepository()
    create_product = CreateProduct(repository, audit_log_repository)

    product = create_product.execute(
        CreateProductCommand(
            name="Mechanical Keyboard",
            sku="key-001",
            price=Decimal("349.90"),
            stock_quantity=10,
        )
    )

    assert product.id == 1
    assert product.name == "Mechanical Keyboard"
    assert product.sku == "KEY-001"
    assert product.price == Decimal("349.90")
    assert product.stock_quantity == 10
    assert product.created_at is not None
    assert repository.get_by_id(product.id) == product
    assert audit_log_repository.list_all()[0].event_type == AuditEventType.PRODUCT_CREATED


def test_reject_duplicate_product_sku() -> None:
    repository = InMemoryProductRepository()
    audit_log_repository = InMemoryAuditLogRepository()
    create_product = CreateProduct(repository, audit_log_repository)
    command = CreateProductCommand(
        name="Mechanical Keyboard",
        sku="key-001",
        price=Decimal("349.90"),
        stock_quantity=10,
    )
    create_product.execute(command)

    with pytest.raises(ProductSkuAlreadyExistsError, match="KEY-001"):
        create_product.execute(
            CreateProductCommand(
                name="Another Keyboard",
                sku="  KEY-001  ",
                price=Decimal("399.90"),
                stock_quantity=5,
            )
        )

    assert len(repository.list_all()) == 1
    assert audit_log_repository.count() == 1
