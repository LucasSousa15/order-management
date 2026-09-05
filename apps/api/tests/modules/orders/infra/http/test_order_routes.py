from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.orders.infra.http.dependencies import (
    get_order_repository,
    get_product_repository,
)
from app.modules.products.domain.entities import Product
from tests.modules.orders.in_memory_repository import InMemoryOrderRepository
from tests.modules.products.in_memory_repository import InMemoryProductRepository


@dataclass(slots=True)
class OrderTestContext:
    client: TestClient
    order_repository: InMemoryOrderRepository
    product_repository: InMemoryProductRepository


@pytest.fixture
def context() -> Iterator[OrderTestContext]:
    order_repository = InMemoryOrderRepository()
    product_repository = InMemoryProductRepository()
    app.dependency_overrides[get_order_repository] = lambda: order_repository
    app.dependency_overrides[get_product_repository] = lambda: product_repository

    with TestClient(app) as client:
        yield OrderTestContext(client, order_repository, product_repository)

    app.dependency_overrides.clear()


def add_product(
    repository: InMemoryProductRepository,
    *,
    sku: str,
    stock_quantity: int,
) -> Product:
    return repository.add(
        Product(
            name=f"Product {sku}",
            sku=sku,
            price=Decimal("25.90"),
            stock_quantity=stock_quantity,
        )
    )


def test_create_order_and_decrement_stock(context: OrderTestContext) -> None:
    first_product = add_product(
        context.product_repository,
        sku="PRO-001",
        stock_quantity=5,
    )
    second_product = add_product(
        context.product_repository,
        sku="PRO-002",
        stock_quantity=3,
    )
    assert first_product.id is not None
    assert second_product.id is not None

    response = context.client.post(
        "/orders",
        json={
            "items": [
                {"product_id": first_product.id, "quantity": 2},
                {"product_id": second_product.id, "quantity": 1},
            ]
        },
    )

    assert response.status_code == 201
    response_body = response.json()
    assert response_body["id"] == 1
    assert response_body["created_at"] is not None
    assert response_body["items"] == [
        {
            "id": 1,
            "product_id": first_product.id,
            "quantity": 2,
            "unit_price": "25.90",
        },
        {
            "id": 2,
            "product_id": second_product.id,
            "quantity": 1,
            "unit_price": "25.90",
        },
    ]
    assert context.product_repository.get_by_id(first_product.id).stock_quantity == 3  # type: ignore[union-attr]
    assert context.product_repository.get_by_id(second_product.id).stock_quantity == 2  # type: ignore[union-attr]


def test_reject_order_when_product_has_no_stock(context: OrderTestContext) -> None:
    product = add_product(
        context.product_repository,
        sku="PRO-001",
        stock_quantity=0,
    )
    assert product.id is not None

    response = context.client.post(
        "/orders",
        json={"items": [{"product_id": product.id, "quantity": 1}]},
    )

    assert response.status_code == 409
    assert str(product.id) in response.json()["detail"]
    assert context.product_repository.get_by_id(product.id) == product
    assert context.order_repository.list_all() == ()


def test_reject_order_when_product_does_not_exist(
    context: OrderTestContext,
) -> None:
    response = context.client.post(
        "/orders",
        json={"items": [{"product_id": 999, "quantity": 1}]},
    )

    assert response.status_code == 404
    assert "999" in response.json()["detail"]


@pytest.mark.parametrize("quantity", [0, -1])
def test_reject_order_with_invalid_quantity(
    context: OrderTestContext,
    quantity: int,
) -> None:
    response = context.client.post(
        "/orders",
        json={"items": [{"product_id": 1, "quantity": quantity}]},
    )

    assert response.status_code == 422


def test_list_orders_with_pagination(context: OrderTestContext) -> None:
    product = add_product(
        context.product_repository,
        sku="PRO-001",
        stock_quantity=3,
    )
    assert product.id is not None

    for _ in range(3):
        response = context.client.post(
            "/orders",
            json={"items": [{"product_id": product.id, "quantity": 1}]},
        )
        assert response.status_code == 201

    response = context.client.get("/orders?page=2&page_size=1")

    assert response.status_code == 200
    response_body = response.json()
    assert [order["id"] for order in response_body["data"]] == [2]
    assert response_body["meta"] == {
        "page": 2,
        "page_size": 1,
        "total_items": 3,
        "total_pages": 3,
        "has_next_page": True,
        "has_previous_page": True,
    }


@pytest.mark.parametrize(
    "query_string",
    ["page=0", "page_size=0", "page_size=101"],
)
def test_reject_invalid_order_pagination(
    context: OrderTestContext,
    query_string: str,
) -> None:
    response = context.client.get(f"/orders?{query_string}")

    assert response.status_code == 422


def test_get_update_and_delete_order(context: OrderTestContext) -> None:
    product = add_product(
        context.product_repository,
        sku="PRO-001",
        stock_quantity=5,
    )
    assert product.id is not None
    created_response = context.client.post(
        "/orders",
        json={"items": [{"product_id": product.id, "quantity": 2}]},
    )
    assert created_response.status_code == 201
    order_id = created_response.json()["id"]

    get_response = context.client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    assert get_response.json() == created_response.json()

    update_response = context.client.put(
        f"/orders/{order_id}",
        json={"items": [{"product_id": product.id, "quantity": 1}]},
    )
    assert update_response.status_code == 200
    assert update_response.json()["items"][0]["quantity"] == 1
    assert context.product_repository.get_by_id(product.id).stock_quantity == 4  # type: ignore[union-attr]

    delete_response = context.client.delete(f"/orders/{order_id}")
    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert context.product_repository.get_by_id(product.id).stock_quantity == 5  # type: ignore[union-attr]
    assert context.client.get(f"/orders/{order_id}").status_code == 404


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_return_not_found_for_missing_order(
    context: OrderTestContext,
    method: str,
) -> None:
    if method == "put":
        response = context.client.put(
            "/orders/999",
            json={"items": [{"product_id": 1, "quantity": 1}]},
        )
    else:
        response = getattr(context.client, method)("/orders/999")

    assert response.status_code == 404
