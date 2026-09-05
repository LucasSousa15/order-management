from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


PositiveInteger = Annotated[int, Field(strict=True, gt=0)]


class OrderItemCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: PositiveInteger
    quantity: PositiveInteger


class OrderCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: Annotated[list[OrderItemCreateRequest], Field(min_length=1)]

    @model_validator(mode="after")
    def validate_unique_products(self) -> Self:
        product_ids = [item.product_id for item in self.items]
        if len(product_ids) != len(set(product_ids)):
            raise ValueError("Each product can appear only once in an order.")
        return self


class OrderUpdateRequest(OrderCreateRequest):
    pass


__all__ = ["OrderCreateRequest", "OrderUpdateRequest"]
