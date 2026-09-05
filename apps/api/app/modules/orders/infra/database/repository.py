from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.core.database.models import OrderItemModel, OrderModel
from app.modules.orders.domain.entities import Order, OrderItem


class SqlAlchemyOrderRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, order: Order) -> Order:
        order_model = OrderModel(
            items=[
                OrderItemModel(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in order.items
            ]
        )
        self._session.add(order_model)
        self._session.flush()
        return self._to_entity(order_model)

    def get_by_id(self, order_id: int) -> Order | None:
        statement = (
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(selectinload(OrderModel.items))
        )
        order_model = self._session.scalar(statement)
        return self._to_entity(order_model) if order_model is not None else None

    def get_by_id_for_update(self, order_id: int) -> Order | None:
        statement = (
            select(OrderModel)
            .where(OrderModel.id == order_id)
            .options(selectinload(OrderModel.items))
            .with_for_update()
        )
        order_model = self._session.scalar(statement)
        return self._to_entity(order_model) if order_model is not None else None

    def list_all(self) -> tuple[Order, ...]:
        statement = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .order_by(OrderModel.id)
        )
        order_models = self._session.scalars(statement).all()
        return tuple(self._to_entity(order_model) for order_model in order_models)

    def list_paginated(self, offset: int, limit: int) -> tuple[Order, ...]:
        statement = (
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .order_by(OrderModel.id)
            .offset(offset)
            .limit(limit)
        )
        order_models = self._session.scalars(statement).all()
        return tuple(self._to_entity(order_model) for order_model in order_models)

    def count(self) -> int:
        statement = select(func.count()).select_from(OrderModel)
        return self._session.scalar(statement) or 0

    def update(self, order: Order) -> Order:
        if order.id is None:
            raise ValueError("A persisted order must have an ID before update.")

        statement = (
            select(OrderModel)
            .where(OrderModel.id == order.id)
            .options(selectinload(OrderModel.items))
        )
        order_model = self._session.scalar(statement)
        if order_model is None:
            raise ValueError(f"Order with ID {order.id} is no longer available.")

        order_model.items.clear()
        self._session.flush()
        order_model.items.extend(
            OrderItemModel(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in order.items
        )
        self._session.flush()
        return self._to_entity(order_model)

    def delete(self, order: Order) -> None:
        if order.id is None:
            raise ValueError("A persisted order must have an ID before deletion.")
        statement = delete(OrderModel).where(OrderModel.id == order.id)
        self._session.execute(statement)
        self._session.flush()

    @staticmethod
    def _to_entity(order_model: OrderModel) -> Order:
        item_models = sorted(order_model.items, key=lambda item: item.id or 0)
        return Order(
            id=order_model.id,
            created_at=order_model.created_at,
            items=tuple(
                OrderItem(
                    id=item_model.id,
                    order_id=item_model.order_id,
                    product_id=item_model.product_id,
                    quantity=item_model.quantity,
                    unit_price=item_model.unit_price,
                )
                for item_model in item_models
            ),
        )


__all__ = ["SqlAlchemyOrderRepository"]
