from decimal import Decimal
from uuid import uuid4

from app.core.database.service import database
from app.modules.products.domain.entities import Product
from app.modules.products.infra.database.repository import (
    SqlAlchemyProductRepository,
)


def test_product_repository_crud() -> None:
    session = database.session()
    repository = SqlAlchemyProductRepository(session)
    sku = f"TEST-{uuid4().hex[:12].upper()}"

    try:
        created_product = repository.add(
            Product(
                name="Mechanical Keyboard",
                sku=sku,
                price=Decimal("349.90"),
                stock_quantity=10,
            )
        )
        assert created_product.id is not None
        assert created_product.created_at is not None
        assert repository.get_by_id(created_product.id) == created_product
        assert repository.get_by_sku(sku.lower()) == created_product
        assert created_product in repository.list_all()

        updated_product = repository.update(
            Product(
                id=created_product.id,
                name="Mechanical Keyboard Pro",
                sku=sku,
                price=Decimal("449.90"),
                stock_quantity=15,
                created_at=created_product.created_at,
            )
        )
        assert updated_product.name == "Mechanical Keyboard Pro"
        assert updated_product.created_at == created_product.created_at

        repository.delete(updated_product)
        assert repository.get_by_id(created_product.id) is None
    finally:
        session.rollback()
        session.close()
