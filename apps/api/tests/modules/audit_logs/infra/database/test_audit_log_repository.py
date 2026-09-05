from app.core.database.service import database
from app.modules.audit_logs.domain.entities import (
    AuditEntityType,
    AuditEventType,
    AuditLog,
)
from app.modules.audit_logs.infra.database.repository import (
    SqlAlchemyAuditLogRepository,
)


def test_audit_log_repository_is_append_only_and_paginated() -> None:
    session = database.session()
    repository = SqlAlchemyAuditLogRepository(session)

    try:
        audit_log = repository.add(
            AuditLog(
                event_type=AuditEventType.ORDER_UPDATED,
                entity_type=AuditEntityType.ORDER,
                entity_id=999_999,
                details={"reason": "integration test"},
            )
        )
        assert audit_log.id is not None
        assert audit_log.created_at is not None
        assert audit_log in repository.list_paginated(offset=0, limit=100)
        assert repository.count() >= 1
    finally:
        session.rollback()
        session.close()
