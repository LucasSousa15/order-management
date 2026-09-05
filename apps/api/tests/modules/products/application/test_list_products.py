from decimal import Decimal

from app.modules.products.application.use_cases import ListProducts
from app.modules.products.domain.entities import Product
from tests.modules.products.in_memory_repository import InMemoryProductRepository


def test_list_products() -> None:
    repository = InMemoryProductRepository()
    first_product = repository.add(
        Product(
            name="Mechanical Keyboard",
            sku="KEY-001",
            price=Decimal("349.90"),
            stock_quantity=10,
        )
    )
    second_product = repository.add(
        Product(
            name="Wireless Mouse",
            sku="MOU-001",
            price=Decimal("149.90"),
            stock_quantity=20,
        )
    )

    products = ListProducts(repository).execute()

    assert products == (first_product, second_product)


def test_list_products_returns_empty_collection() -> None:
    repository = InMemoryProductRepository()

    products = ListProducts(repository).execute()

    assert products == ()
