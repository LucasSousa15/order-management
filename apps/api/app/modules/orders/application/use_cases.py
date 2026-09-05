from dataclasses import dataclass, replace

from app.core.pagination import PageRequest, PageResult
from app.modules.orders.application.errors import (
    InsufficientStockError,
    OrderNotFoundError,
    OrderProductNotFoundError,
)
from app.modules.orders.domain.entities import Order, OrderItem, OrderItemSelection
from app.modules.orders.domain.repositories import OrderRepository
from app.modules.products.domain.entities import Product
from app.modules.products.domain.repositories import ProductRepository


@dataclass(frozen=True, slots=True)
class CreateOrderCommand:
    items: tuple[OrderItemSelection, ...]


@dataclass(frozen=True, slots=True)
class UpdateOrderCommand:
    order_id: int
    items: tuple[OrderItemSelection, ...]


class CreateOrder:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
    ) -> None:
        self._order_repository = order_repository
        self._product_repository = product_repository

    def execute(self, command: CreateOrderCommand) -> Order:
        product_ids = tuple(item.product_id for item in command.items)
        products = self._product_repository.get_by_ids_for_update(product_ids)
        products_by_id = {
            product.id: product for product in products if product.id is not None
        }

        self._ensure_products_exist(command.items, products_by_id)
        self._ensure_stock_is_available(command.items, products_by_id)

        order = Order(
            items=tuple(
                OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=products_by_id[item.product_id].price,
                )
                for item in command.items
            )
        )
        persisted_order = self._order_repository.add(order)

        for item in command.items:
            product = products_by_id[item.product_id]
            self._product_repository.update(
                replace(
                    product,
                    stock_quantity=product.stock_quantity - item.quantity,
                )
            )

        return persisted_order

    @staticmethod
    def _ensure_products_exist(
        items: tuple[OrderItemSelection, ...],
        products_by_id: dict[int, Product],
    ) -> None:
        for item in items:
            if item.product_id not in products_by_id:
                raise OrderProductNotFoundError(item.product_id)

    @staticmethod
    def _ensure_stock_is_available(
        items: tuple[OrderItemSelection, ...],
        products_by_id: dict[int, Product],
    ) -> None:
        for item in items:
            product = products_by_id[item.product_id]
            if product.stock_quantity < item.quantity:
                raise InsufficientStockError(
                    product_id=item.product_id,
                    requested_quantity=item.quantity,
                    available_quantity=product.stock_quantity,
                )


class ListOrders:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def execute(self, page: PageRequest) -> PageResult[Order]:
        orders = self._repository.list_paginated(
            offset=page.offset,
            limit=page.page_size,
        )
        return PageResult(
            items=tuple(orders),
            page=page.page,
            page_size=page.page_size,
            total_items=self._repository.count(),
        )


class GetOrder:
    def __init__(self, repository: OrderRepository) -> None:
        self._repository = repository

    def execute(self, order_id: int) -> Order:
        order = self._repository.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)
        return order


class UpdateOrder:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
    ) -> None:
        self._order_repository = order_repository
        self._product_repository = product_repository

    def execute(self, command: UpdateOrderCommand) -> Order:
        current_order = self._order_repository.get_by_id_for_update(
            command.order_id
        )
        if current_order is None:
            raise OrderNotFoundError(command.order_id)

        previous_quantities = {
            item.product_id: item.quantity for item in current_order.items
        }
        requested_quantities = {
            item.product_id: item.quantity for item in command.items
        }
        involved_product_ids = tuple(
            sorted(previous_quantities.keys() | requested_quantities.keys())
        )
        products = self._product_repository.get_by_ids_for_update(
            involved_product_ids
        )
        products_by_id = {
            product.id: product for product in products if product.id is not None
        }

        CreateOrder._ensure_products_exist(command.items, products_by_id)
        updated_order = Order(
            id=current_order.id,
            created_at=current_order.created_at,
            items=tuple(
                OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=products_by_id[item.product_id].price,
                )
                for item in command.items
            ),
        )

        for item in updated_order.items:
            product = products_by_id[item.product_id]
            available_quantity = (
                product.stock_quantity
                + previous_quantities.get(item.product_id, 0)
            )
            if available_quantity < item.quantity:
                raise InsufficientStockError(
                    product_id=item.product_id,
                    requested_quantity=item.quantity,
                    available_quantity=available_quantity,
                )

        persisted_order = self._order_repository.update(updated_order)
        for product_id in involved_product_ids:
            product = products_by_id[product_id]
            reconciled_stock = (
                product.stock_quantity
                + previous_quantities.get(product_id, 0)
                - requested_quantities.get(product_id, 0)
            )
            if reconciled_stock != product.stock_quantity:
                self._product_repository.update(
                    replace(product, stock_quantity=reconciled_stock)
                )

        return persisted_order


class DeleteOrder:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
    ) -> None:
        self._order_repository = order_repository
        self._product_repository = product_repository

    def execute(self, order_id: int) -> None:
        order = self._order_repository.get_by_id_for_update(order_id)
        if order is None:
            raise OrderNotFoundError(order_id)

        product_ids = tuple(sorted(item.product_id for item in order.items))
        products = self._product_repository.get_by_ids_for_update(product_ids)
        products_by_id = {
            product.id: product for product in products if product.id is not None
        }

        for item in order.items:
            product = products_by_id[item.product_id]
            self._product_repository.update(
                replace(
                    product,
                    stock_quantity=product.stock_quantity + item.quantity,
                )
            )

        self._order_repository.delete(order)


__all__ = [
    "CreateOrder",
    "CreateOrderCommand",
    "DeleteOrder",
    "GetOrder",
    "ListOrders",
    "UpdateOrder",
    "UpdateOrderCommand",
]
