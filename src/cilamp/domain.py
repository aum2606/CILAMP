"""Provider-independent identity and access domain objects."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class EmployeeStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


@dataclass(frozen=True)
class Department:
    name: str


@dataclass(frozen=True)
class Group:
    name: str


@dataclass(frozen=True)
class Application:
    name: str
    sensitivity: str


@dataclass(frozen=True)
class Permission:
    name: str
    description: str


@dataclass(frozen=True)
class JobRole:
    name: str
    department: str
    groups: tuple[str, ...]
    applications: tuple[str, ...]
    permissions: tuple[str, ...]
    privileged: bool = False


@dataclass(frozen=True)
class Employee:
    employee_id: str
    display_name: str
    email: str
    department: str
    job_role: str
    status: EmployeeStatus = EmployeeStatus.ACTIVE


@dataclass(frozen=True)
class EffectiveAccess:
    groups: tuple[str, ...]
    applications: tuple[str, ...]
    permissions: tuple[str, ...]


@dataclass(frozen=True)
class AccessChanges:
    groups: tuple[str, ...] = ()
    applications: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()


@dataclass(frozen=True)
class LifecyclePlan:
    operation: str
    employee_id: str
    before_employee: Employee | None
    after_employee: Employee
    before_access: EffectiveAccess
    after_access: EffectiveAccess
    to_remove: AccessChanges
    to_add: AccessChanges
    reason: str


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    timestamp: datetime
    actor: str
    target_identity: str
    action: str
    old_state: str
    new_state: str
    result: str
    reason: str
    correlation_id: str


class RiskLevel(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"


@dataclass(frozen=True)
class AccessFinding:
    category: str
    risk: RiskLevel
    entitlement_type: str
    entitlement: str
    explanation: str
    suggested_remediation: str


@dataclass(frozen=True)
class AccessReview:
    employee: Employee
    expected: EffectiveAccess
    actual: EffectiveAccess
    findings: tuple[AccessFinding, ...]
    privileged: bool

    @property
    def compliant(self) -> bool:
        return not self.findings

    @property
    def privilege_creep(self) -> bool:
        return any(
            finding.category
            in {"EXCESSIVE_PRIVILEGE", "PRIVILEGE_CREEP", "UNAUTHORIZED_ACCESS"}
            for finding in self.findings
        )


class FindingStatus(StrEnum):
    OPEN = "OPEN"
    REMEDIATED = "REMEDIATED"


@dataclass(frozen=True)
class SecurityFinding:
    finding_id: str
    created_at: datetime
    target_identity: str
    scenario_type: str
    title: str
    description: str
    risk: RiskLevel
    status: FindingStatus
    evidence: dict[str, str]
    recommendation: str
    correlation_id: str
    resolved_at: datetime | None = None
    resolution: str = ""


@dataclass(frozen=True)
class SecurityScenarioPlan:
    scenario_type: str
    target_identity: str
    title: str
    description: str
    risk: RiskLevel
    evidence: dict[str, str]
    recommendation: str
    to_remove: AccessChanges = AccessChanges()
    to_add: AccessChanges = AccessChanges()
    new_status: EmployeeStatus | None = None
    observed_action: str = "SECURITY_CONTROL_CHECK"
    observed_result: str = "FAILURE"
