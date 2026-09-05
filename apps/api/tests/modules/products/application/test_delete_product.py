from decimal import Decimal

import pytest

from app.modules.products.application.errors import ProductNotFoundError
from app.modules.products.application.use_cases import DeleteProduct
from app.modules.products.domain.entities import Product
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

    result = DeleteProduct(repository).execute(product.id)

    assert result is None
    assert repository.get_by_id(product.id) is None


def test_reject_delete_when_product_does_not_exist() -> None:
    repository = InMemoryProductRepository()

    with pytest.raises(ProductNotFoundError, match="999"):
        DeleteProduct(repository).execute(999)
