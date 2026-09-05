class OrderApplicationError(Exception):
    pass


class OrderNotFoundError(OrderApplicationError):
    def __init__(self, order_id: int) -> None:
        super().__init__(f'Order with ID "{order_id}" was not found.')
        self.order_id = order_id


class OrderProductNotFoundError(OrderApplicationError):
    def __init__(self, product_id: int) -> None:
        super().__init__(f'Product with ID "{product_id}" was not found.')
        self.product_id = product_id


class InsufficientStockError(OrderApplicationError):
    def __init__(
        self,
        product_id: int,
        requested_quantity: int,
        available_quantity: int,
    ) -> None:
        super().__init__(
            f'Insufficient stock for product with ID "{product_id}": '
            f"requested {requested_quantity}, available {available_quantity}."
        )
        self.product_id = product_id
        self.requested_quantity = requested_quantity
        self.available_quantity = available_quantity


__all__ = [
    "InsufficientStockError",
    "OrderApplicationError",
    "OrderNotFoundError",
    "OrderProductNotFoundError",
]
