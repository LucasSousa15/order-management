from collections.abc import Sequence
from typing import Protocol

from app.modules.audit_logs.domain.entities import AuditLog


class AuditLogRepository(Protocol):
    def add(self, audit_log: AuditLog) -> AuditLog:
        ...

    def list_paginated(self, offset: int, limit: int) -> Sequence[AuditLog]:
        ...

    def count(self) -> int:
        ...


__all__ = ["AuditLogRepository"]
