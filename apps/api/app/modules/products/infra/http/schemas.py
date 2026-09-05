from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


ProductName = Annotated[str, Field(min_length=1, max_length=120)]
ProductSku = Annotated[str, Field(min_length=1, max_length=64)]
ProductPrice = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
StockQuantity = Annotated[int, Field(strict=True, ge=0)]


class ProductWriteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: ProductName
    sku: ProductSku
    price: ProductPrice
    stock_quantity: StockQuantity


class ProductCreateRequest(ProductWriteRequest):
    pass


class ProductUpdateRequest(ProductWriteRequest):
    pass


__all__ = [
    "ProductCreateRequest",
    "ProductUpdateRequest",
]
