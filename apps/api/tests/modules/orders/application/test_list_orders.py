from decimal import Decimal

from app.core.pagination import PageRequest
from app.modules.orders.application.use_cases import ListOrders
from app.modules.orders.domain.entities import Order, OrderItem
from tests.modules.orders.in_memory_repository import InMemoryOrderRepository


def add_order(repository: InMemoryOrderRepository, product_id: int) -> Order:
    return repository.add(
        Order(
            items=(
                OrderItem(
                    product_id=product_id,
                    quantity=1,
                    unit_price=Decimal("25.90"),
                ),
            )
        )
    )


def test_list_orders_with_pagination() -> None:
    repository = InMemoryOrderRepository()
    first_order = add_order(repository, product_id=1)
    second_order = add_order(repository, product_id=2)
    third_order = add_order(repository, product_id=3)

    first_page = ListOrders(repository).execute(
        PageRequest(page=1, page_size=2)
    )
    second_page = ListOrders(repository).execute(
        PageRequest(page=2, page_size=2)
    )

    assert first_page.items == (first_order, second_order)
    assert first_page.total_items == 3
    assert first_page.total_pages == 2
    assert first_page.has_next_page is True
    assert second_page.items == (third_order,)
    assert second_page.has_previous_page is True


def test_list_orders_returns_empty_page() -> None:
    result = ListOrders(InMemoryOrderRepository()).execute(PageRequest())

    assert result.items == ()
    assert result.total_items == 0
    assert result.total_pages == 0
