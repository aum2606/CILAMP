"""Phase and module status presented by the Project Control Center."""

from __future__ import annotations

from dataclasses import dataclass


PROJECT_NAME = "Cloud Identity Lifecycle & Access Management Platform"
PROJECT_SHORT_NAME = "CILAMP"
CURRENT_PHASE = "Phase 4 — Security & Audit Center"


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
    ModuleStatus("Entra ID", "Not Connected", "Microsoft identity lab connector"),
    ModuleStatus("Azure", "Not Connected", "Azure RBAC and workload identity"),
    ModuleStatus("AWS", "Not Connected", "AWS IAM roles and policies"),
    ModuleStatus("Terraform", "Not Started", "Infrastructure as Code representation"),
)


RECENT_MILESTONES = (
    "Security & Audit Center and troubleshooting workflows implemented",
    "Six auditable IAM security scenarios added in simulation mode",
    "RBAC access-review and least-privilege policy engine implemented",
)


def completed_module_count() -> int:
    return sum(item.status == "Complete" for item in MODULE_STATUSES)
