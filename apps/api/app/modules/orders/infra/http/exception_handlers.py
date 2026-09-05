from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.modules.orders.application.errors import (
    InsufficientStockError,
    OrderNotFoundError,
    OrderProductNotFoundError,
)
from app.modules.orders.domain.entities import OrderValidationError


async def order_product_not_found_handler(
    _request: Request,
    error: OrderProductNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(error)},
    )


async def insufficient_stock_handler(
    _request: Request,
    error: InsufficientStockError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(error)},
    )


async def order_validation_handler(
    _request: Request,
    error: OrderValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": str(error)},
    )


async def order_not_found_handler(
    _request: Request,
    error: OrderNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(error)},
    )


def register_order_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(OrderNotFoundError, order_not_found_handler)
    app.add_exception_handler(
        OrderProductNotFoundError,
        order_product_not_found_handler,
    )
    app.add_exception_handler(InsufficientStockError, insufficient_stock_handler)
    app.add_exception_handler(OrderValidationError, order_validation_handler)


__all__ = ["register_order_exception_handlers"]
