from decimal import Decimal

import pytest

from app.modules.products.domain.entities import Product, ProductValidationError


def test_create_valid_product() -> None:
    product = Product(
        name="  Mechanical Keyboard  ",
        sku="  key-001  ",
        price=Decimal("349.90"),
        stock_quantity=10,
    )

    assert product.id is None
    assert product.name == "Mechanical Keyboard"
    assert product.sku == "KEY-001"
    assert product.price == Decimal("349.90")
    assert product.stock_quantity == 10
    assert product.created_at is None


@pytest.mark.parametrize("name", ["", "   "])
def test_reject_blank_product_name(name: str) -> None:
    with pytest.raises(ProductValidationError, match="name"):
        Product(
            name=name,
            sku="KEY-001",
            price=Decimal("349.90"),
            stock_quantity=10,
        )


@pytest.mark.parametrize("sku", ["", "   "])
def test_reject_blank_product_sku(sku: str) -> None:
    with pytest.raises(ProductValidationError, match="SKU"):
        Product(
            name="Mechanical Keyboard",
            sku=sku,
            price=Decimal("349.90"),
            stock_quantity=10,
        )


@pytest.mark.parametrize("price", [Decimal("0"), Decimal("-0.01")])
def test_reject_non_positive_product_price(price: Decimal) -> None:
    with pytest.raises(ProductValidationError, match="price"):
        Product(
            name="Mechanical Keyboard",
            sku="KEY-001",
            price=price,
            stock_quantity=10,
        )


def test_reject_non_decimal_product_price() -> None:
    with pytest.raises(ProductValidationError, match="Decimal"):
        Product(
            name="Mechanical Keyboard",
            sku="KEY-001",
            price=349.90,  # type: ignore[arg-type]
            stock_quantity=10,
        )


def test_reject_negative_product_stock() -> None:
    with pytest.raises(ProductValidationError, match="stock"):
        Product(
            name="Mechanical Keyboard",
            sku="KEY-001",
            price=Decimal("349.90"),
            stock_quantity=-1,
        )
