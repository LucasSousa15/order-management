from typing import Annotated

from fastapi import APIRouter, Query

from app.core.pagination import PageRequest
from app.modules.audit_logs.application.use_cases import ListAuditLogs
from app.modules.audit_logs.infra.http.dependencies import AuditLogRepositoryDependency
from app.modules.audit_logs.infra.http.view_models import AuditLogListViewModel


router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("", response_model=AuditLogListViewModel)
def list_audit_logs(
    repository: AuditLogRepositoryDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> AuditLogListViewModel:
    result = ListAuditLogs(repository).execute(
        PageRequest(page=page, page_size=page_size)
    )
    return AuditLogListViewModel.from_page(result)


__all__ = ["router"]
