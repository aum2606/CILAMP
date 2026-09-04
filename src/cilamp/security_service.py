"""Application service for security scenarios, cases, and remediation."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from cilamp.access_review_service import remediate_employee, review_employee
from cilamp.domain import EffectiveAccess, FindingStatus, SecurityFinding
from cilamp.repository import (
    execute_security_scenario,
    get_assigned_access,
    get_employee,
    list_employees,
    list_security_findings,
    resolve_security_findings,
)
from cilamp.security import SCENARIO_BY_TYPE, build_scenario_plan


def eligible_employees(path: Path, scenario_type: str):
    definition = SCENARIO_BY_TYPE[scenario_type]
    if definition.target_rule == "WORKLOAD":
        return []
    employees = list_employees(path, status="ACTIVE")
    if definition.target_rule == "ACTIVE_DEVELOPER":
        return [employee for employee in employees if employee.job_role == "Developer"]
    if definition.target_rule == "ACTIVE_FINANCE_ANALYST":
        return [employee for employee in employees if employee.job_role == "Finance Analyst"]
    return employees


def preview_security_scenario(path: Path, scenario_type: str, employee_id: str | None):
    if scenario_type == "INSECURE_WORKLOAD_CREDENTIAL":
        return build_scenario_plan(scenario_type, None, _empty_access())
    if not employee_id:
        raise ValueError("Select an employee for this scenario.")
    employee = get_employee(path, employee_id)
    if employee is None:
        raise ValueError("Employee does not exist.")
    return build_scenario_plan(
        scenario_type, employee, get_assigned_access(path, employee_id)
    )


def create_security_scenario(path: Path, plan):
    return execute_security_scenario(path, plan)


def get_security_finding(path: Path, finding_id: str) -> SecurityFinding:
    finding = next(
        (item for item in list_security_findings(path) if item.finding_id == finding_id),
        None,
    )
    if finding is None:
        raise ValueError("Security finding does not exist.")
    return finding


def remediate_security_finding(
    path: Path,
    finding_id: str,
    actor: str = "simulation.security-analyst",
) -> tuple[str, int]:
    finding = get_security_finding(path, finding_id)
    if finding.status != FindingStatus.OPEN:
        raise ValueError("Security finding is already remediated.")

    if finding.target_identity.startswith("workload:"):
        correlation_id = str(uuid4())
        resolution = (
            "Simulated static credential removed; managed/federated workload identity required."
        )
    else:
        review = review_employee(path, finding.target_identity)
        if review.compliant:
            correlation_id = str(uuid4())
        else:
            correlation_id = remediate_employee(path, review, actor=actor)
        resolution = "Actual assignments reconciled to the current role/status baseline."

    count = resolve_security_findings(
        path,
        finding.target_identity,
        actor,
        resolution,
        correlation_id,
    )
    return correlation_id, count


def _empty_access():
    return EffectiveAccess((), (), ())
