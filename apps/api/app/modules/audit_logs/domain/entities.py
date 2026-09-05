from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class AuditEventType(StrEnum):
    PRODUCT_CREATED = "PRODUCT_CREATED"
    PRODUCT_UPDATED = "PRODUCT_UPDATED"
    PRODUCT_DELETED = "PRODUCT_DELETED"
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_UPDATED = "ORDER_UPDATED"
    ORDER_DELETED = "ORDER_DELETED"
    STOCK_MOVEMENT = "STOCK_MOVEMENT"


class AuditEntityType(StrEnum):
    PRODUCT = "PRODUCT"
    ORDER = "ORDER"


@dataclass(frozen=True, slots=True)
class AuditLog:
    event_type: AuditEventType
    entity_type: AuditEntityType
    entity_id: int
    details: dict[str, Any] = field(default_factory=dict)
    id: int | None = None
    created_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.entity_id <= 0:
            raise ValueError("Audit log entity ID must be positive.")
        object.__setattr__(self, "details", dict(self.details))


__all__ = ["AuditEntityType", "AuditEventType", "AuditLog"]
