from app.core.pagination import PageRequest, PageResult
from app.modules.audit_logs.domain.entities import AuditLog
from app.modules.audit_logs.domain.repositories import AuditLogRepository


class ListAuditLogs:
    def __init__(self, repository: AuditLogRepository) -> None:
        self._repository = repository

    def execute(self, page: PageRequest) -> PageResult[AuditLog]:
        audit_logs = self._repository.list_paginated(
            offset=page.offset,
            limit=page.page_size,
        )
        return PageResult(
            items=tuple(audit_logs),
            page=page.page,
            page_size=page.page_size,
            total_items=self._repository.count(),
        )


__all__ = ["ListAuditLogs"]
