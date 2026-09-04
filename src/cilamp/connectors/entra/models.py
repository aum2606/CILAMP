"""Display-safe records exchanged by Entra connector implementations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EntraUser:
    object_id: str
    display_name: str
    user_principal_name: str
    account_enabled: bool
    department: str = ""
    job_title: str = ""


@dataclass(frozen=True)
class EntraGroup:
    object_id: str
    display_name: str
    description: str = ""
    security_enabled: bool = True
    group_type: str = "Security"


@dataclass(frozen=True)
class EntraServicePrincipal:
    object_id: str
    display_name: str
    application_id: str
    principal_type: str
    account_enabled: bool = True


@dataclass(frozen=True)
class EntraDirectoryAudit:
    record_id: str
    activity_at: datetime
    activity: str
    result: str
    initiated_by: str
    target: str


@dataclass(frozen=True)
class EntraSnapshot:
    users: tuple[EntraUser, ...]
    groups: tuple[EntraGroup, ...]
    service_principals: tuple[EntraServicePrincipal, ...]
    directory_audits: tuple[EntraDirectoryAudit, ...] = ()
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class EntraSyncState:
    status: str
    mode: str
    tenant_label: str
    last_synced_at: datetime | None
    user_count: int
    group_count: int
    service_principal_count: int
    audit_count: int
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class EntraOperation:
    operation_id: str
    timestamp: datetime
    mode: str
    action: str
    target: str
    result: str
    details: str
    correlation_id: str
