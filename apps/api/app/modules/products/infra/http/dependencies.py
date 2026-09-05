from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database.service import get_session
from app.modules.products.domain.repositories import ProductRepository
from app.modules.products.infra.database.repository import (
    SqlAlchemyProductRepository,
)


SessionDependency = Annotated[Session, Depends(get_session)]


def get_product_repository(session: SessionDependency) -> ProductRepository:
    return SqlAlchemyProductRepository(session)


ProductRepositoryDependency = Annotated[
    ProductRepository,
    Depends(get_product_repository),
]


__all__ = ["ProductRepositoryDependency", "get_product_repository"]
