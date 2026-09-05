from typing import Never

from sqlalchemy import delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database.models import ProductModel
from app.modules.products.application.errors import (
    ProductInUseError,
    ProductSkuAlreadyExistsError,
)
from app.modules.products.domain.entities import Product


class SqlAlchemyProductRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, product: Product) -> Product:
        product_model = ProductModel(
            name=product.name,
            sku=product.sku,
            price=product.price,
            stock_quantity=product.stock_quantity,
        )
        self._session.add(product_model)

        try:
            self._session.flush()
        except IntegrityError as error:
            self._raise_mapped_integrity_error(error, product)

        return self._to_entity(product_model)

    def get_by_id(self, product_id: int) -> Product | None:
        statement = select(ProductModel).where(ProductModel.id == product_id)
        product_model = self._session.scalar(statement)
        return self._to_entity(product_model) if product_model is not None else None

    def get_by_sku(self, sku: str) -> Product | None:
        normalized_sku = sku.strip().upper()
        statement = select(ProductModel).where(ProductModel.sku == normalized_sku)
        product_model = self._session.scalar(statement)
        return self._to_entity(product_model) if product_model is not None else None

    def list_all(self) -> tuple[Product, ...]:
        statement = select(ProductModel).order_by(ProductModel.id)
        product_models = self._session.scalars(statement).all()
        return tuple(self._to_entity(product_model) for product_model in product_models)

    def update(self, product: Product) -> Product:
        if product.id is None:
            raise ValueError("A persisted product must have an ID before update.")

        statement = (
            update(ProductModel)
            .where(ProductModel.id == product.id)
            .values(
                name=product.name,
                sku=product.sku,
                price=product.price,
                stock_quantity=product.stock_quantity,
            )
            .returning(ProductModel)
        )

        try:
            product_model = self._session.scalars(statement).one()
            self._session.flush()
        except IntegrityError as error:
            self._raise_mapped_integrity_error(error, product)

        return self._to_entity(product_model)

    def delete(self, product: Product) -> None:
        if product.id is None:
            raise ValueError("A persisted product must have an ID before deletion.")

        statement = delete(ProductModel).where(ProductModel.id == product.id)
        try:
            self._session.execute(statement)
            self._session.flush()
        except IntegrityError as error:
            if self._constraint_name(error) == "order_items_product_id_fkey":
                raise ProductInUseError(product.id) from error
            raise

    @staticmethod
    def _to_entity(product_model: ProductModel) -> Product:
        return Product(
            id=product_model.id,
            name=product_model.name,
            sku=product_model.sku,
            price=product_model.price,
            stock_quantity=product_model.stock_quantity,
            created_at=product_model.created_at,
        )

    @classmethod
    def _raise_mapped_integrity_error(
        cls,
        error: IntegrityError,
        product: Product,
    ) -> Never:
        if cls._constraint_name(error) == "ix_products_sku":
            raise ProductSkuAlreadyExistsError(product.sku) from error
        raise error

    @staticmethod
    def _constraint_name(error: IntegrityError) -> str | None:
        diagnostic = getattr(error.orig, "diag", None)
        return getattr(diagnostic, "constraint_name", None)


__all__ = ["SqlAlchemyProductRepository"]
