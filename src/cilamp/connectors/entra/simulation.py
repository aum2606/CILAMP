"""Deterministic Entra-shaped adapter backed by the fictional organization."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from cilamp.connectors.entra.models import (
    EntraDirectoryAudit,
    EntraGroup,
    EntraServicePrincipal,
    EntraSnapshot,
    EntraUser,
)
from cilamp.iam_catalog import APPLICATIONS, GROUP_NAMES
from cilamp.repository import get_assigned_access, list_employees


def _sim_id(kind: str, value: str) -> str:
    return f"sim-{kind}-{value.lower().replace(' ', '-')}"


class SimulationEntraConnector:
    """Expose local identities through the same contract used by Microsoft Graph."""

    mode = "SIMULATION"

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def check_connection(self) -> str:
        return "SIMULATED"

    def read_snapshot(self) -> EntraSnapshot:
        users = tuple(
            EntraUser(
                object_id=_sim_id("user", employee.employee_id),
                display_name=employee.display_name,
                user_principal_name=employee.email,
                account_enabled=employee.status.value == "ACTIVE",
                department=employee.department,
                job_title=employee.job_role,
            )
            for employee in list_employees(self.database_path)
        )
        groups = tuple(
            EntraGroup(
                object_id=_sim_id("group", name),
                display_name=name,
                description="CILAMP simulated role-based group",
            )
            for name in GROUP_NAMES
        )
        principals = tuple(
            EntraServicePrincipal(
                object_id=_sim_id("sp", application.name),
                display_name=application.name,
                application_id=_sim_id("app", application.name),
                principal_type="Application",
            )
            for application in APPLICATIONS
        )
        audit = EntraDirectoryAudit(
            record_id="sim-audit-snapshot",
            activity_at=datetime.now(timezone.utc),
            activity="Synchronize simulated Entra directory",
            result="success",
            initiated_by="simulation.entra-operator",
            target="Simulation tenant",
        )
        return EntraSnapshot(
            users=users,
            groups=groups,
            service_principals=principals,
            directory_audits=(audit,),
            limitations=(
                "Conditional Access, PIM, MFA registration, and Lifecycle Workflows are conceptual only in simulation.",
            ),
        )

    def list_group_members(self, group_id: str) -> tuple[EntraUser, ...]:
        prefix = "sim-group-"
        if not group_id.startswith(prefix):
            return ()
        result = []
        for employee in list_employees(self.database_path):
            access = get_assigned_access(self.database_path, employee.employee_id)
            if any(_sim_id("group", name) == group_id for name in access.groups):
                result.append(
                    EntraUser(
                        _sim_id("user", employee.employee_id),
                        employee.display_name,
                        employee.email,
                        employee.status.value == "ACTIVE",
                        employee.department,
                        employee.job_role,
                    )
                )
        return tuple(result)

    def update_user(self, user_id: str, *, department: str, job_title: str) -> None:
        return None

    def add_group_member(self, group_id: str, user_id: str) -> None:
        return None

    def remove_group_member(self, group_id: str, user_id: str) -> None:
        return None
