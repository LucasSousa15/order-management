from dataclasses import dataclass, replace
from decimal import Decimal

from app.core.pagination import PageRequest, PageResult
from app.modules.audit_logs.domain.entities import (
    AuditEntityType,
    AuditEventType,
    AuditLog,
)
from app.modules.audit_logs.domain.repositories import AuditLogRepository
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


def _items_snapshot(order: Order) -> list[dict[str, str | int]]:
    return [
        {
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": str(item.unit_price),
        }
        for item in order.items
    ]


def _order_total(order: Order) -> str:
    return str(
        sum(
            (item.unit_price * item.quantity for item in order.items),
            Decimal("0"),
        )
    )


def _record_order_event(
    repository: AuditLogRepository,
    event_type: AuditEventType,
    order: Order,
    previous_order: Order | None = None,
) -> None:
    if order.id is None:
        raise ValueError("A persisted order must have an ID for auditing.")
    details: dict[str, object] = {
        "items": _items_snapshot(order),
        "total": _order_total(order),
    }
    if previous_order is not None:
        details = {
            "before": {
                "items": _items_snapshot(previous_order),
                "total": _order_total(previous_order),
            },
            "after": details,
        }
    repository.add(
        AuditLog(
            event_type=event_type,
            entity_type=AuditEntityType.ORDER,
            entity_id=order.id,
            details=details,
        )
    )


def _record_stock_movement(
    repository: AuditLogRepository,
    product: Product,
    new_quantity: int,
    order_id: int | None,
    reason: AuditEventType,
) -> None:
    if product.id is None or order_id is None:
        raise ValueError("Persisted product and order IDs are required for auditing.")
    repository.add(
        AuditLog(
            event_type=AuditEventType.STOCK_MOVEMENT,
            entity_type=AuditEntityType.PRODUCT,
            entity_id=product.id,
            details={
                "reason": reason.value,
                "order_id": order_id,
                "previous_quantity": product.stock_quantity,
                "change": new_quantity - product.stock_quantity,
                "new_quantity": new_quantity,
            },
        )
    )


class CreateOrder:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._order_repository = order_repository
        self._product_repository = product_repository
        self._audit_log_repository = audit_log_repository

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
            updated_product = self._product_repository.update(
                replace(
                    product,
                    stock_quantity=product.stock_quantity - item.quantity,
                )
            )
            _record_stock_movement(
                repository=self._audit_log_repository,
                product=product,
                new_quantity=updated_product.stock_quantity,
                order_id=persisted_order.id,
                reason=AuditEventType.ORDER_CREATED,
            )

        _record_order_event(
            repository=self._audit_log_repository,
            event_type=AuditEventType.ORDER_CREATED,
            order=persisted_order,
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
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._order_repository = order_repository
        self._product_repository = product_repository
        self._audit_log_repository = audit_log_repository

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
                updated_product = self._product_repository.update(
                    replace(product, stock_quantity=reconciled_stock)
                )
                _record_stock_movement(
                    repository=self._audit_log_repository,
                    product=product,
                    new_quantity=updated_product.stock_quantity,
                    order_id=persisted_order.id,
                    reason=AuditEventType.ORDER_UPDATED,
                )

        _record_order_event(
            repository=self._audit_log_repository,
            event_type=AuditEventType.ORDER_UPDATED,
            order=persisted_order,
            previous_order=current_order,
        )

        return persisted_order


class DeleteOrder:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        audit_log_repository: AuditLogRepository,
    ) -> None:
        self._order_repository = order_repository
        self._product_repository = product_repository
        self._audit_log_repository = audit_log_repository

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
            updated_product = self._product_repository.update(
                replace(
                    product,
                    stock_quantity=product.stock_quantity + item.quantity,
                )
            )
            _record_stock_movement(
                repository=self._audit_log_repository,
                product=product,
                new_quantity=updated_product.stock_quantity,
                order_id=order.id,
                reason=AuditEventType.ORDER_DELETED,
            )

        self._order_repository.delete(order)
        _record_order_event(
            repository=self._audit_log_repository,
            event_type=AuditEventType.ORDER_DELETED,
            order=order,
        )


__all__ = [
    "CreateOrder",
    "CreateOrderCommand",
    "DeleteOrder",
    "GetOrder",
    "ListOrders",
    "UpdateOrder",
    "UpdateOrderCommand",
]
