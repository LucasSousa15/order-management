from fastapi import APIRouter, Response, status

from app.modules.products.application.use_cases import (
    CreateProduct,
    CreateProductCommand,
    DeleteProduct,
    GetProduct,
    ListProducts,
    UpdateProduct,
    UpdateProductCommand,
)
from app.modules.products.domain.entities import Product
from app.modules.products.infra.http.dependencies import (
    ProductRepositoryDependency,
)
from app.modules.products.infra.http.schemas import (
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
)


router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    request: ProductCreateRequest,
    repository: ProductRepositoryDependency,
) -> Product:
    return CreateProduct(repository).execute(
        CreateProductCommand(
            name=request.name,
            sku=request.sku,
            price=request.price,
            stock_quantity=request.stock_quantity,
        )
    )


@router.get("", response_model=list[ProductResponse])
def list_products(repository: ProductRepositoryDependency) -> list[Product]:
    return list(ListProducts(repository).execute())


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    repository: ProductRepositoryDependency,
) -> Product:
    return GetProduct(repository).execute(product_id)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    request: ProductUpdateRequest,
    repository: ProductRepositoryDependency,
) -> Product:
    return UpdateProduct(repository).execute(
        UpdateProductCommand(
            product_id=product_id,
            name=request.name,
            sku=request.sku,
            price=request.price,
            stock_quantity=request.stock_quantity,
        )
    )


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_product(
    product_id: int,
    repository: ProductRepositoryDependency,
) -> Response:
    DeleteProduct(repository).execute(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


__all__ = ["router"]
