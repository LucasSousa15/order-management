from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.core.http.pagination import PaginationMetaViewModel
from app.core.pagination import PageResult
from app.modules.audit_logs.domain.entities import AuditLog


class AuditLogViewModel(BaseModel):
    id: int
    event_type: str
    entity_type: str
    entity_id: int
    details: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_entity(cls, audit_log: AuditLog) -> "AuditLogViewModel":
        if audit_log.id is None or audit_log.created_at is None:
            raise ValueError("Only persisted audit logs can be exposed by the API.")
        return cls(
            id=audit_log.id,
            event_type=audit_log.event_type.value,
            entity_type=audit_log.entity_type.value,
            entity_id=audit_log.entity_id,
            details=audit_log.details,
            created_at=audit_log.created_at,
        )


class AuditLogListViewModel(BaseModel):
    data: list[AuditLogViewModel]
    meta: PaginationMetaViewModel

    @classmethod
    def from_page(cls, page: PageResult[AuditLog]) -> "AuditLogListViewModel":
        return cls(
            data=[AuditLogViewModel.from_entity(item) for item in page.items],
            meta=PaginationMetaViewModel.from_page(page),
        )


__all__ = ["AuditLogListViewModel", "AuditLogViewModel"]
