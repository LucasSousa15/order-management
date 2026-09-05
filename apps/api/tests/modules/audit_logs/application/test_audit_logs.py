from app.core.pagination import PageRequest
from app.modules.audit_logs.application.use_cases import ListAuditLogs
from app.modules.audit_logs.domain.entities import (
    AuditEntityType,
    AuditEventType,
    AuditLog,
)
from tests.modules.audit_logs.in_memory_repository import InMemoryAuditLogRepository


def add_log(repository: InMemoryAuditLogRepository, entity_id: int) -> AuditLog:
    return repository.add(
        AuditLog(
            event_type=AuditEventType.PRODUCT_CREATED,
            entity_type=AuditEntityType.PRODUCT,
            entity_id=entity_id,
            details={"sku": f"PRO-{entity_id:03}"},
        )
    )


def test_list_audit_logs_from_newest_with_pagination() -> None:
    repository = InMemoryAuditLogRepository()
    first_log = add_log(repository, 1)
    second_log = add_log(repository, 2)
    third_log = add_log(repository, 3)

    first_page = ListAuditLogs(repository).execute(
        PageRequest(page=1, page_size=2)
    )
    second_page = ListAuditLogs(repository).execute(
        PageRequest(page=2, page_size=2)
    )

    assert first_page.items == (third_log, second_log)
    assert second_page.items == (first_log,)
    assert first_page.total_items == 3
    assert first_page.total_pages == 2
