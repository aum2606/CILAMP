"""Display-safe AWS IAM and audit records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AwsResource:
    arn: str
    name: str
    resource_type: str
    region: str


@dataclass(frozen=True)
class AwsRole:
    arn: str
    name: str
    path: str
    trusted_principals: tuple[str, ...]
    credential_mode: str


@dataclass(frozen=True)
class AwsPolicyStatement:
    sid: str
    effect: str
    actions: tuple[str, ...]
    resources: tuple[str, ...]
    has_conditions: bool = False


@dataclass(frozen=True)
class AwsPolicy:
    arn: str
    name: str
    source: str
    statements: tuple[AwsPolicyStatement, ...]


@dataclass(frozen=True)
class AwsRolePolicyBinding:
    role_arn: str
    policy_arn: str


@dataclass(frozen=True)
class AwsCloudTrailEvent:
    event_id: str
    event_time: datetime
    event_name: str
    username: str
    resource_name: str


@dataclass(frozen=True)
class AwsSnapshot:
    resources: tuple[AwsResource, ...]
    roles: tuple[AwsRole, ...]
    policies: tuple[AwsPolicy, ...]
    bindings: tuple[AwsRolePolicyBinding, ...]
    cloudtrail_events: tuple[AwsCloudTrailEvent, ...]
    caller_arn: str
    limitations: tuple[str, ...] = ()


@dataclass(frozen=True)
class AwsAccessDecision:
    role_arn: str
    role_name: str
    resource_arn: str
    resource_name: str
    action: str
    decision: str
    matched_policies: tuple[str, ...]
    rationale: str


@dataclass(frozen=True)
class AwsSyncState:
    status: str
    mode: str
    account_label: str
    region: str
    last_synced_at: datetime | None
    resource_count: int
    role_count: int
    policy_count: int
    event_count: int
    caller_arn: str
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class AwsOperation:
    operation_id: str
    timestamp: datetime
    mode: str
    action: str
    target: str
    result: str
    details: str
    correlation_id: str
