from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.core.pagination import PageRequest
from app.modules.orders.application.use_cases import (
    CreateOrder,
    CreateOrderCommand,
    DeleteOrder,
    GetOrder,
    ListOrders,
    UpdateOrder,
    UpdateOrderCommand,
)
from app.modules.orders.domain.entities import OrderItemSelection
from app.modules.orders.infra.http.dependencies import (
    OrderRepositoryDependency,
    ProductRepositoryDependency,
)
from app.modules.orders.infra.http.schemas import (
    OrderCreateRequest,
    OrderUpdateRequest,
)
from app.modules.orders.infra.http.view_models import (
    OrderListViewModel,
    OrderViewModel,
)


router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderViewModel, status_code=status.HTTP_201_CREATED)
def create_order(
    request: OrderCreateRequest,
    order_repository: OrderRepositoryDependency,
    product_repository: ProductRepositoryDependency,
) -> OrderViewModel:
    order = CreateOrder(order_repository, product_repository).execute(
        CreateOrderCommand(
            items=tuple(
                OrderItemSelection(
                    product_id=item.product_id,
                    quantity=item.quantity,
                )
                for item in request.items
            )
        )
    )
    return OrderViewModel.from_entity(order)


@router.get("", response_model=OrderListViewModel)
def list_orders(
    order_repository: OrderRepositoryDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> OrderListViewModel:
    result = ListOrders(order_repository).execute(
        PageRequest(page=page, page_size=page_size)
    )
    return OrderListViewModel.from_page(result)


@router.get("/{order_id}", response_model=OrderViewModel)
def get_order(
    order_id: int,
    order_repository: OrderRepositoryDependency,
) -> OrderViewModel:
    order = GetOrder(order_repository).execute(order_id)
    return OrderViewModel.from_entity(order)


@router.put("/{order_id}", response_model=OrderViewModel)
def update_order(
    order_id: int,
    request: OrderUpdateRequest,
    order_repository: OrderRepositoryDependency,
    product_repository: ProductRepositoryDependency,
) -> OrderViewModel:
    order = UpdateOrder(order_repository, product_repository).execute(
        UpdateOrderCommand(
            order_id=order_id,
            items=tuple(
                OrderItemSelection(
                    product_id=item.product_id,
                    quantity=item.quantity,
                )
                for item in request.items
            ),
        )
    )
    return OrderViewModel.from_entity(order)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_order(
    order_id: int,
    order_repository: OrderRepositoryDependency,
    product_repository: ProductRepositoryDependency,
) -> Response:
    DeleteOrder(order_repository, product_repository).execute(order_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


__all__ = ["router"]
