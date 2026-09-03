"""Phase and module status presented by the Project Control Center."""

from __future__ import annotations

from dataclasses import dataclass


PROJECT_NAME = "Cloud Identity Lifecycle & Access Management Platform"
PROJECT_SHORT_NAME = "CILAMP"
CURRENT_PHASE = "Phase 0 — Foundation"


@dataclass(frozen=True)
class ModuleStatus:
    module: str
    status: str
    purpose: str


MODULE_STATUSES = (
    ModuleStatus("Organization Model", "Not Started", "Employees, roles, groups, and applications"),
    ModuleStatus("JML Engine", "Not Started", "Joiner, Mover, and Leaver workflows"),
    ModuleStatus("RBAC", "Not Started", "Role-based access and least-privilege checks"),
    ModuleStatus("Audit", "Not Started", "Identity and access event history"),
    ModuleStatus("Entra ID", "Not Connected", "Microsoft identity lab connector"),
    ModuleStatus("Azure", "Not Connected", "Azure RBAC and workload identity"),
    ModuleStatus("AWS", "Not Connected", "AWS IAM roles and policies"),
    ModuleStatus("Terraform", "Not Started", "Infrastructure as Code representation"),
)


RECENT_MILESTONES = (
    "Phase 0 repository and security guardrails established",
    "Modular Python and SQLite foundation created",
    "Streamlit Project Control Center made available",
)


def completed_module_count() -> int:
    return sum(item.status == "Complete" for item in MODULE_STATUSES)
