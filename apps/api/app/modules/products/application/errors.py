class ProductApplicationError(Exception):
    pass


class ProductSkuAlreadyExistsError(ProductApplicationError):
    def __init__(self, sku: str) -> None:
        super().__init__(f'A product with SKU "{sku}" already exists.')
        self.sku = sku


class ProductNotFoundError(ProductApplicationError):
    def __init__(self, product_id: int) -> None:
        super().__init__(f'Product with ID "{product_id}" was not found.')
        self.product_id = product_id


class ProductInUseError(ProductApplicationError):
    def __init__(self, product_id: int) -> None:
        super().__init__(
            f'Product with ID "{product_id}" cannot be deleted because it is in use.'
        )
        self.product_id = product_id


__all__ = [
    "ProductApplicationError",
    "ProductInUseError",
    "ProductNotFoundError",
    "ProductSkuAlreadyExistsError",
]
