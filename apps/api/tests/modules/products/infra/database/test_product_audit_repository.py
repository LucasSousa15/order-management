from decimal import Decimal
from uuid import uuid4

from app.core.database.service import database
from app.modules.audit_logs.domain.entities import AuditEventType
from app.modules.audit_logs.infra.database.repository import SqlAlchemyAuditLogRepository
from app.modules.products.application.use_cases import (
    CreateProduct,
    CreateProductCommand,
    DeleteProduct,
    UpdateProduct,
    UpdateProductCommand,
)
from app.modules.products.infra.database.repository import (
    SqlAlchemyProductRepository,
)


def test_product_changes_are_persisted_with_audit_logs() -> None:
    session = database.session()
    product_repository = SqlAlchemyProductRepository(session)
    audit_log_repository = SqlAlchemyAuditLogRepository(session)
    sku = f"PRODUCT-AUDIT-{uuid4().hex[:12].upper()}"

    try:
        product = CreateProduct(
            product_repository,
            audit_log_repository,
        ).execute(
            CreateProductCommand(
                name="Product audit integration test",
                sku=sku,
                price=Decimal("25.90"),
                stock_quantity=3,
            )
        )
        assert product.id is not None

        UpdateProduct(product_repository, audit_log_repository).execute(
            UpdateProductCommand(
                product_id=product.id,
                name=product.name,
                sku=product.sku,
                price=Decimal("29.90"),
                stock_quantity=5,
            )
        )
        DeleteProduct(product_repository, audit_log_repository).execute(product.id)

        assert [
            audit_log.event_type
            for audit_log in reversed(
                audit_log_repository.list_paginated(offset=0, limit=4)
            )
        ] == [
            AuditEventType.PRODUCT_CREATED,
            AuditEventType.PRODUCT_UPDATED,
            AuditEventType.STOCK_MOVEMENT,
            AuditEventType.PRODUCT_DELETED,
        ]
    finally:
        session.rollback()
        session.close()
