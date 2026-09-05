from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


class ProductValidationError(ValueError):
    pass


@dataclass(slots=True)
class Product:
    name: str
    sku: str
    price: Decimal
    stock_quantity: int
    id: int | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        self.name = self._normalize_name(self.name)
        self.sku = self._normalize_sku(self.sku)
        self._validate_price(self.price)
        self._validate_stock(self.stock_quantity)

    @staticmethod
    def _normalize_name(name: str) -> str:
        if not isinstance(name, str) or not name.strip():
            raise ProductValidationError("Product name must not be blank.")

        normalized_name = name.strip()
        if len(normalized_name) > 120:
            raise ProductValidationError(
                "Product name must contain at most 120 characters."
            )

        return normalized_name

    @staticmethod
    def _normalize_sku(sku: str) -> str:
        if not isinstance(sku, str) or not sku.strip():
            raise ProductValidationError("Product SKU must not be blank.")

        normalized_sku = sku.strip().upper()
        if len(normalized_sku) > 64:
            raise ProductValidationError(
                "Product SKU must contain at most 64 characters."
            )

        return normalized_sku

    @staticmethod
    def _validate_price(price: Decimal) -> None:
        if not isinstance(price, Decimal):
            raise ProductValidationError("Product price must be a Decimal.")

        if not price.is_finite() or price <= Decimal("0"):
            raise ProductValidationError("Product price must be positive.")

    @staticmethod
    def _validate_stock(stock_quantity: int) -> None:
        if not isinstance(stock_quantity, int) or isinstance(stock_quantity, bool):
            raise ProductValidationError(
                "Product stock quantity must be an integer."
            )

        if stock_quantity < 0:
            raise ProductValidationError(
                "Product stock quantity must not be negative."
            )


__all__ = ["Product", "ProductValidationError"]
