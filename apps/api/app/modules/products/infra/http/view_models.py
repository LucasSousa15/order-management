from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.core.http.pagination import PaginationMetaViewModel
from app.core.pagination import PageResult
from app.modules.products.domain.entities import Product


class ProductViewModel(BaseModel):
    id: int
    name: str
    sku: str
    price: Decimal
    stock_quantity: int
    created_at: datetime

    @classmethod
    def from_entity(cls, product: Product) -> "ProductViewModel":
        if product.id is None or product.created_at is None:
            raise ValueError("Only persisted products can be exposed by the API.")
        return cls(
            id=product.id,
            name=product.name,
            sku=product.sku,
            price=product.price,
            stock_quantity=product.stock_quantity,
            created_at=product.created_at,
        )


class ProductListViewModel(BaseModel):
    data: list[ProductViewModel]
    meta: PaginationMetaViewModel

    @classmethod
    def from_page(cls, page: PageResult[Product]) -> "ProductListViewModel":
        return cls(
            data=[ProductViewModel.from_entity(product) for product in page.items],
            meta=PaginationMetaViewModel.from_page(page),
        )


__all__ = ["ProductListViewModel", "ProductViewModel"]
