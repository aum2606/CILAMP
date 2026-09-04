"""Application service for access review scenarios and remediation."""

from __future__ import annotations

from pathlib import Path

from cilamp.domain import AccessReview, RiskLevel
from cilamp.policy import evaluate_access
from cilamp.repository import (
    LifecycleConflict,
    add_simulated_permission,
    get_assigned_access,
    get_employee,
    list_employees,
    reconcile_access,
)


def review_employee(path: Path, employee_id: str) -> AccessReview:
    employee = get_employee(path, employee_id)
    if employee is None:
        raise ValueError("Employee does not exist.")
    return evaluate_access(employee, get_assigned_access(path, employee_id))


def review_all(path: Path) -> list[AccessReview]:
    return [
        evaluate_access(employee, get_assigned_access(path, employee.employee_id))
        for employee in list_employees(path)
    ]


def review_summary(reviews: list[AccessReview]) -> dict[str, int]:
    return {
        "identities": len(reviews),
        "compliant": sum(review.compliant for review in reviews),
        "identities_with_findings": sum(not review.compliant for review in reviews),
        "findings": sum(len(review.findings) for review in reviews),
        "critical": sum(
            finding.risk == RiskLevel.CRITICAL
            for review in reviews
            for finding in review.findings
        ),
        "privileged": sum(review.privileged for review in reviews),
        "privilege_creep": sum(review.privilege_creep for review in reviews),
    }


def create_developer_admin_scenario(
    path: Path, employee_id: str, actor: str = "simulation.security-admin"
) -> str:
    employee = get_employee(path, employee_id)
    if employee is None or employee.job_role != "Developer":
        raise ValueError("Select an active Developer for this scenario.")
    return add_simulated_permission(
        path,
        employee_id,
        "platform.administrator",
        actor,
        "Deliberate Phase 3 excessive-privilege scenario",
    )


def remediate_employee(
    path: Path,
    review: AccessReview,
    actor: str = "simulation.security-admin",
) -> str:
    if review.compliant:
        raise LifecycleConflict("The selected identity is already compliant.")
    return reconcile_access(
        path,
        review.employee.employee_id,
        review.actual,
        review.expected,
        actor,
        "Approved simulation remediation to role baseline",
    )
