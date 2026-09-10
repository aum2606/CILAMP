"""Phase and module status presented by the Project Control Center."""

from __future__ import annotations

from dataclasses import dataclass


PROJECT_NAME = "Cloud Identity Lifecycle & Access Management Platform"
PROJECT_SHORT_NAME = "CILAMP"
CURRENT_PHASE = "Phase 7 — AWS IAM Integration"


@dataclass(frozen=True)
class ModuleStatus:
    module: str
    status: str
    purpose: str


MODULE_STATUSES = (
    ModuleStatus("Organization Model", "Complete", "Employees, roles, groups, and applications"),
    ModuleStatus("JML Engine", "Complete", "Joiner, Mover, and Leaver workflows"),
    ModuleStatus("RBAC", "Complete", "Role-based access and least-privilege checks"),
    ModuleStatus("Audit", "Complete", "Security events, investigations, and audit history"),
    ModuleStatus("Entra ID", "Complete", "Simulation and guarded Microsoft Graph lab connector"),
    ModuleStatus("Azure", "Complete", "Azure resource scopes, RBAC, and managed identities"),
    ModuleStatus("AWS", "Complete", "AWS IAM roles, policies, STS, and CloudTrail"),
    ModuleStatus("Terraform", "Not Started", "Infrastructure as Code representation"),
)


RECENT_MILESTONES = (
    "AWS IAM roles, policy evaluation, STS, S3, and CloudTrail center implemented",
    "Azure resource, RBAC scope, and effective-access center implemented",
    "Managed identity and credential-free workload pattern demonstrated",
)


def completed_module_count() -> int:
    return sum(item.status == "Complete" for item in MODULE_STATUSES)
