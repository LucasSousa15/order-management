from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.core.pagination import PageRequest
from app.modules.audit_logs.infra.http.dependencies import AuditLogRepositoryDependency
from app.modules.products.application.use_cases import (
    CreateProduct,
    CreateProductCommand,
    DeleteProduct,
    GetProduct,
    ListProducts,
    UpdateProduct,
    UpdateProductCommand,
)
from app.modules.products.infra.http.dependencies import (
    ProductRepositoryDependency,
)
from app.modules.products.infra.http.schemas import (
    ProductCreateRequest,
    ProductUpdateRequest,
)
from app.modules.products.infra.http.view_models import (
    ProductListViewModel,
    ProductViewModel,
)


router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductViewModel, status_code=status.HTTP_201_CREATED)
def create_product(
    request: ProductCreateRequest,
    repository: ProductRepositoryDependency,
    audit_log_repository: AuditLogRepositoryDependency,
) -> ProductViewModel:
    product = CreateProduct(repository, audit_log_repository).execute(
        CreateProductCommand(
            name=request.name,
            sku=request.sku,
            price=request.price,
            stock_quantity=request.stock_quantity,
        )
    )
    return ProductViewModel.from_entity(product)


@router.get("", response_model=ProductListViewModel)
def list_products(
    repository: ProductRepositoryDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ProductListViewModel:
    result = ListProducts(repository).execute(
        PageRequest(page=page, page_size=page_size)
    )
    return ProductListViewModel.from_page(result)


@router.get("/{product_id}", response_model=ProductViewModel)
def get_product(
    product_id: int,
    repository: ProductRepositoryDependency,
) -> ProductViewModel:
    product = GetProduct(repository).execute(product_id)
    return ProductViewModel.from_entity(product)


@router.put("/{product_id}", response_model=ProductViewModel)
def update_product(
    product_id: int,
    request: ProductUpdateRequest,
    repository: ProductRepositoryDependency,
    audit_log_repository: AuditLogRepositoryDependency,
) -> ProductViewModel:
    product = UpdateProduct(repository, audit_log_repository).execute(
        UpdateProductCommand(
            product_id=product_id,
            name=request.name,
            sku=request.sku,
            price=request.price,
            stock_quantity=request.stock_quantity,
        )
    )
    return ProductViewModel.from_entity(product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_product(
    product_id: int,
    repository: ProductRepositoryDependency,
    audit_log_repository: AuditLogRepositoryDependency,
) -> Response:
    DeleteProduct(repository, audit_log_repository).execute(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


__all__ = ["router"]
