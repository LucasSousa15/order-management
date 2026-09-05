from decimal import Decimal

import pytest

from app.modules.products.application.errors import ProductNotFoundError
from app.modules.products.application.use_cases import DeleteProduct
from app.modules.products.domain.entities import Product
from app.modules.audit_logs.domain.entities import AuditEventType
from tests.modules.audit_logs.in_memory_repository import InMemoryAuditLogRepository
from tests.modules.products.in_memory_repository import InMemoryProductRepository


def test_delete_product() -> None:
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
    result = DeleteProduct(repository, audit_log_repository).execute(product.id)

    assert result is None
    assert repository.get_by_id(product.id) is None
    assert audit_log_repository.list_all()[0].event_type == AuditEventType.PRODUCT_DELETED


def test_reject_delete_when_product_does_not_exist() -> None:
    repository = InMemoryProductRepository()

    with pytest.raises(ProductNotFoundError, match="999"):
        DeleteProduct(repository, InMemoryAuditLogRepository()).execute(999)
