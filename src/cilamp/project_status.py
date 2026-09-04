"""Phase and module status presented by the Project Control Center."""

from __future__ import annotations

from dataclasses import dataclass


PROJECT_NAME = "Cloud Identity Lifecycle & Access Management Platform"
PROJECT_SHORT_NAME = "CILAMP"
CURRENT_PHASE = "Phase 3 — RBAC & Access Review"


@dataclass(frozen=True)
class ModuleStatus:
    module: str
    status: str
    purpose: str


MODULE_STATUSES = (
    ModuleStatus("Organization Model", "Complete", "Employees, roles, groups, and applications"),
    ModuleStatus("JML Engine", "Complete", "Joiner, Mover, and Leaver workflows"),
    ModuleStatus("RBAC", "Complete", "Role-based access and least-privilege checks"),
    ModuleStatus("Audit", "Foundation Added", "Lifecycle audit events; full center in Phase 4"),
    ModuleStatus("Entra ID", "Not Connected", "Microsoft identity lab connector"),
    ModuleStatus("Azure", "Not Connected", "Azure RBAC and workload identity"),
    ModuleStatus("AWS", "Not Connected", "AWS IAM roles and policies"),
    ModuleStatus("Terraform", "Not Started", "Infrastructure as Code representation"),
)


RECENT_MILESTONES = (
    "RBAC access-review and least-privilege policy engine implemented",
    "Excess privilege scenario detection and simulation remediation added",
    "Simulated Joiner, Mover, and Leaver workflows implemented",
)


def completed_module_count() -> int:
    return sum(item.status == "Complete" for item in MODULE_STATUSES)
