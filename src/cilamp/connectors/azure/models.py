"""Display-safe Azure resource and authorization records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AzureResource:
    resource_id: str
    name: str
    resource_type: str
    resource_group: str
    location: str


@dataclass(frozen=True)
class AzureIdentity:
    principal_id: str
    display_name: str
    identity_type: str
    source_resource: str
    credential_mode: str


@dataclass(frozen=True)
class AzureRoleAssignment:
    assignment_id: str
    principal_id: str
    principal_name: str
    principal_type: str
    role_definition_id: str
    role_name: str
    scope: str


@dataclass(frozen=True)
class AzureSnapshot:
    resources: tuple[AzureResource, ...]
    identities: tuple[AzureIdentity, ...]
    role_assignments: tuple[AzureRoleAssignment, ...]
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class AzureAccessDecision:
    principal_id: str
    principal_name: str
    resource_id: str
    resource_name: str
    action: str
    decision: str
    matched_roles: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class AzureSyncState:
    status: str
    mode: str
    subscription_label: str
    resource_group: str
    last_synced_at: datetime | None
    resource_count: int
    identity_count: int
    assignment_count: int
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class AzureOperation:
    operation_id: str
    timestamp: datetime
    mode: str
    action: str
    target: str
    result: str
    details: str
    correlation_id: str
