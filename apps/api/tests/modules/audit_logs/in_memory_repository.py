from dataclasses import replace
from datetime import UTC, datetime

from app.modules.audit_logs.domain.entities import AuditLog


class InMemoryAuditLogRepository:
    def __init__(self) -> None:
        self._audit_logs: dict[int, AuditLog] = {}
        self._next_id = 1

    def add(self, audit_log: AuditLog) -> AuditLog:
        persisted_log = replace(
            audit_log,
            id=self._next_id,
            created_at=datetime.now(UTC),
        )
        self._audit_logs[self._next_id] = persisted_log
        self._next_id += 1
        return persisted_log

    def list_paginated(self, offset: int, limit: int) -> tuple[AuditLog, ...]:
        audit_logs = tuple(reversed(self._audit_logs.values()))
        return audit_logs[offset : offset + limit]

    def count(self) -> int:
        return len(self._audit_logs)

    def list_all(self) -> tuple[AuditLog, ...]:
        return tuple(self._audit_logs.values())
