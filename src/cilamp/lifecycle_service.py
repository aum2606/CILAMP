"""Application service that coordinates lifecycle plans and local persistence."""

from __future__ import annotations

import re
from pathlib import Path

from cilamp.domain import Employee, EmployeeStatus, LifecyclePlan
from cilamp.iam_catalog import ROLE_BY_NAME
from cilamp.lifecycle import LifecycleValidationError, plan_joiner, plan_leaver, plan_mover
from cilamp.repository import (
    email_exists,
    execute_lifecycle_plan,
    get_assigned_access,
    get_employee,
    next_employee_id,
)


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def preview_joiner(
    path: Path,
    display_name: str,
    email: str,
    job_role: str,
    reason: str,
) -> LifecyclePlan:
    clean_name = " ".join(display_name.split())
    clean_email = email.strip().lower()
    if len(clean_name) < 2:
        raise LifecycleValidationError("Enter a fictional employee name.")
    if not EMAIL_PATTERN.fullmatch(clean_email):
        raise LifecycleValidationError("Enter a valid fictional email address.")
    if email_exists(path, clean_email):
        raise LifecycleValidationError("That email address already belongs to an identity.")
    role = ROLE_BY_NAME.get(job_role)
    if role is None:
        raise LifecycleValidationError(f"Unknown job role: {job_role}")
    employee = Employee(
        employee_id=next_employee_id(path),
        display_name=clean_name,
        email=clean_email,
        department=role.department,
        job_role=role.name,
        status=EmployeeStatus.ACTIVE,
    )
    return plan_joiner(employee, reason)


def preview_mover(
    path: Path, employee_id: str, new_job_role: str, reason: str
) -> LifecyclePlan:
    employee = get_employee(path, employee_id)
    if employee is None:
        raise LifecycleValidationError("Employee does not exist.")
    return plan_mover(employee, get_assigned_access(path, employee_id), new_job_role, reason)


def preview_leaver(path: Path, employee_id: str, reason: str) -> LifecyclePlan:
    employee = get_employee(path, employee_id)
    if employee is None:
        raise LifecycleValidationError("Employee does not exist.")
    return plan_leaver(employee, get_assigned_access(path, employee_id), reason)


def execute(path: Path, plan: LifecyclePlan, actor: str = "simulation.operator") -> str:
    """Execute a confirmed simulation plan and return its correlation ID."""

    return execute_lifecycle_plan(path, plan, actor)
