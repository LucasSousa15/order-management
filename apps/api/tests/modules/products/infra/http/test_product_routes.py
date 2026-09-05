from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.products.infra.http.dependencies import get_product_repository
from tests.modules.products.in_memory_repository import InMemoryProductRepository


@pytest.fixture
def client() -> Iterator[TestClient]:
    repository = InMemoryProductRepository()
    app.dependency_overrides[get_product_repository] = lambda: repository

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_product_crud(client: TestClient) -> None:
    create_response = client.post(
        "/products",
        json={
            "name": "Mechanical Keyboard",
            "sku": "key-001",
            "price": "349.90",
            "stock_quantity": 10,
        },
    )

    assert create_response.status_code == 201
    created_product = create_response.json()
    assert created_product["id"] == 1
    assert created_product["sku"] == "KEY-001"
    assert created_product["price"] == "349.90"

    list_response = client.get("/products")
    assert list_response.status_code == 200
    assert list_response.json() == {
        "data": [created_product],
        "meta": {
            "page": 1,
            "page_size": 20,
            "total_items": 1,
            "total_pages": 1,
            "has_next_page": False,
            "has_previous_page": False,
        },
    }

    get_response = client.get("/products/1")
    assert get_response.status_code == 200
    assert get_response.json() == created_product

    update_response = client.put(
        "/products/1",
        json={
            "name": "Mechanical Keyboard Pro",
            "sku": "key-001",
            "price": "449.90",
            "stock_quantity": 15,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json() == {
        **created_product,
        "name": "Mechanical Keyboard Pro",
        "price": "449.90",
        "stock_quantity": 15,
    }

    delete_response = client.delete("/products/1")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    missing_response = client.get("/products/1")
    assert missing_response.status_code == 404
    assert "1" in missing_response.json()["detail"]


def test_reject_duplicate_sku(client: TestClient) -> None:
    payload = {
        "name": "Mechanical Keyboard",
        "sku": "KEY-001",
        "price": "349.90",
        "stock_quantity": 10,
    }
    assert client.post("/products", json=payload).status_code == 201

    response = client.post(
        "/products",
        json={**payload, "name": "Another Keyboard", "sku": " key-001 "},
    )

    assert response.status_code == 409
    assert "KEY-001" in response.json()["detail"]


def test_reject_invalid_product_payload(client: TestClient) -> None:
    response = client.post(
        "/products",
        json={
            "name": " ",
            "sku": "KEY-001",
            "price": "0",
            "stock_quantity": -1,
        },
    )

    assert response.status_code == 422


def test_paginate_products(client: TestClient) -> None:
    for index in range(1, 4):
        response = client.post(
            "/products",
            json={
                "name": f"Product {index}",
                "sku": f"PRO-{index:03}",
                "price": "10.00",
                "stock_quantity": 1,
            },
        )
        assert response.status_code == 201

    response = client.get("/products?page=2&page_size=1")

    assert response.status_code == 200
    response_body = response.json()
    assert [product["id"] for product in response_body["data"]] == [2]
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
def test_reject_invalid_pagination(
    client: TestClient,
    query_string: str,
) -> None:
    response = client.get(f"/products?{query_string}")

    assert response.status_code == 422
