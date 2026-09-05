from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.modules.products.application.errors import (
    ProductInUseError,
    ProductNotFoundError,
    ProductSkuAlreadyExistsError,
)
from app.modules.products.domain.entities import ProductValidationError


async def product_not_found_handler(
    _request: Request,
    error: ProductNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(error)},
    )


async def product_conflict_handler(
    _request: Request,
    error: ProductSkuAlreadyExistsError | ProductInUseError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(error)},
    )


async def product_validation_handler(
    _request: Request,
    error: ProductValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": str(error)},
    )


def register_product_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ProductNotFoundError, product_not_found_handler)
    app.add_exception_handler(ProductSkuAlreadyExistsError, product_conflict_handler)
    app.add_exception_handler(ProductInUseError, product_conflict_handler)
    app.add_exception_handler(ProductValidationError, product_validation_handler)


__all__ = ["register_product_exception_handlers"]
