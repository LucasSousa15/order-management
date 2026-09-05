from decimal import Decimal

import pytest

from app.modules.products.application.errors import ProductNotFoundError
from app.modules.products.application.use_cases import GetProduct
from app.modules.products.domain.entities import Product
from tests.modules.products.in_memory_repository import InMemoryProductRepository


def test_get_product_by_id() -> None:
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

    found_product = GetProduct(repository).execute(product.id)

    assert found_product == product


def test_reject_get_when_product_does_not_exist() -> None:
    repository = InMemoryProductRepository()

    with pytest.raises(ProductNotFoundError, match="999"):
        GetProduct(repository).execute(999)
