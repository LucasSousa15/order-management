from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.audit_logs.domain.entities import (
    AuditEntityType,
    AuditEventType,
    AuditLog,
)
from app.modules.audit_logs.infra.http.dependencies import get_audit_log_repository
from tests.modules.audit_logs.in_memory_repository import InMemoryAuditLogRepository


@pytest.fixture
def client() -> Iterator[TestClient]:
    repository = InMemoryAuditLogRepository()
    repository.add(
        AuditLog(
            event_type=AuditEventType.PRODUCT_CREATED,
            entity_type=AuditEntityType.PRODUCT,
            entity_id=10,
            details={"sku": "PRO-010"},
        )
    )
    app.dependency_overrides[get_audit_log_repository] = lambda: repository

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_list_audit_logs(client: TestClient) -> None:
    list_response = client.get("/audit-logs?page=1&page_size=20")

    assert list_response.status_code == 200
    response_body = list_response.json()
    assert response_body["meta"]["total_items"] == 1
    assert response_body["data"][0]["event_type"] == "PRODUCT_CREATED"
    assert response_body["data"][0]["details"] == {"sku": "PRO-010"}



def test_does_not_expose_get_audit_log_by_id(client: TestClient) -> None:
    response = client.get("/audit-logs/1")

    assert response.status_code == 404
