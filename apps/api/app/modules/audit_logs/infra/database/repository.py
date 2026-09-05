from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database.models import AuditLogModel
from app.modules.audit_logs.domain.entities import (
    AuditEntityType,
    AuditEventType,
    AuditLog,
)


class SqlAlchemyAuditLogRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, audit_log: AuditLog) -> AuditLog:
        audit_log_model = AuditLogModel(
            event_type=audit_log.event_type.value,
            entity_type=audit_log.entity_type.value,
            entity_id=audit_log.entity_id,
            details=audit_log.details,
        )
        self._session.add(audit_log_model)
        self._session.flush()
        return self._to_entity(audit_log_model)

    def list_paginated(self, offset: int, limit: int) -> tuple[AuditLog, ...]:
        statement = (
            select(AuditLogModel)
            .order_by(AuditLogModel.id.desc())
            .offset(offset)
            .limit(limit)
        )
        audit_log_models = self._session.scalars(statement).all()
        return tuple(
            self._to_entity(audit_log_model)
            for audit_log_model in audit_log_models
        )

    def count(self) -> int:
        statement = select(func.count()).select_from(AuditLogModel)
        return self._session.scalar(statement) or 0

    @staticmethod
    def _to_entity(audit_log_model: AuditLogModel) -> AuditLog:
        return AuditLog(
            id=audit_log_model.id,
            event_type=AuditEventType(audit_log_model.event_type),
            entity_type=AuditEntityType(audit_log_model.entity_type),
            entity_id=audit_log_model.entity_id,
            details=audit_log_model.details,
            created_at=audit_log_model.created_at,
        )


__all__ = ["SqlAlchemyAuditLogRepository"]
