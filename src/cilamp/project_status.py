"""Phase and module status presented by the Project Control Center."""

from __future__ import annotations

from dataclasses import dataclass


PROJECT_NAME = "Cloud Identity Lifecycle & Access Management Platform"
PROJECT_SHORT_NAME = "CILAMP"
CURRENT_PHASE = "Phase 5 — Microsoft Entra ID Integration"


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
    ModuleStatus("Azure", "Not Connected", "Azure RBAC and workload identity"),
    ModuleStatus("AWS", "Not Connected", "AWS IAM roles and policies"),
    ModuleStatus("Terraform", "Not Started", "Infrastructure as Code representation"),
)


RECENT_MILESTONES = (
    "Microsoft Entra simulation and guarded live-lab connector implemented",
    "Entra users, groups, memberships, service principals, and audit cache added",
    "Security & Audit Center and troubleshooting workflows implemented",
)


def completed_module_count() -> int:
    return sum(item.status == "Complete" for item in MODULE_STATUSES)
