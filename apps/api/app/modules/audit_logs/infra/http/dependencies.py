from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database.service import get_session
from app.modules.audit_logs.domain.repositories import AuditLogRepository
from app.modules.audit_logs.infra.database.repository import (
    SqlAlchemyAuditLogRepository,
)


SessionDependency = Annotated[Session, Depends(get_session)]


def get_audit_log_repository(
    session: SessionDependency,
) -> AuditLogRepository:
    return SqlAlchemyAuditLogRepository(session)


AuditLogRepositoryDependency = Annotated[
    AuditLogRepository,
    Depends(get_audit_log_repository),
]


__all__ = ["AuditLogRepositoryDependency", "get_audit_log_repository"]
