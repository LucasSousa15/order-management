from decimal import Decimal

from app.core.pagination import PageRequest
from app.modules.products.application.use_cases import ListProducts
from app.modules.products.domain.entities import Product
from tests.modules.products.in_memory_repository import InMemoryProductRepository


def test_list_products_with_pagination() -> None:
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
    third_product = repository.add(
        Product(
            name="USB-C Hub",
            sku="HUB-001",
            price=Decimal("199.90"),
            stock_quantity=5,
        )
    )

    first_page = ListProducts(repository).execute(
        PageRequest(page=1, page_size=2)
    )
    second_page = ListProducts(repository).execute(
        PageRequest(page=2, page_size=2)
    )

    assert first_page.items == (first_product, second_product)
    assert first_page.total_items == 3
    assert first_page.total_pages == 2
    assert first_page.has_previous_page is False
    assert first_page.has_next_page is True
    assert second_page.items == (third_product,)
    assert second_page.has_previous_page is True
    assert second_page.has_next_page is False


def test_list_products_returns_empty_collection() -> None:
    repository = InMemoryProductRepository()

    products = ListProducts(repository).execute(PageRequest())

    assert products.items == ()
    assert products.total_items == 0
    assert products.total_pages == 0
