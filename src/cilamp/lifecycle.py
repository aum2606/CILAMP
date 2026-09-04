"""Provider-independent Joiner, Mover, and Leaver planning rules."""

from __future__ import annotations

from dataclasses import replace

from cilamp.domain import AccessChanges, EffectiveAccess, Employee, EmployeeStatus, LifecyclePlan
from cilamp.iam_catalog import ROLE_BY_NAME


class LifecycleValidationError(ValueError):
    """Raised when a requested lifecycle transition violates IAM rules."""


EMPTY_ACCESS = EffectiveAccess((), (), ())


def expected_access(job_role: str) -> EffectiveAccess:
    try:
        role = ROLE_BY_NAME[job_role]
    except KeyError as error:
        raise LifecycleValidationError(f"Unknown job role: {job_role}") from error
    return EffectiveAccess(role.groups, role.applications, role.permissions)


def _changes(left: EffectiveAccess, right: EffectiveAccess) -> AccessChanges:
    """Return entitlements in left that are absent from right."""

    return AccessChanges(
        groups=tuple(sorted(set(left.groups) - set(right.groups))),
        applications=tuple(sorted(set(left.applications) - set(right.applications))),
        permissions=tuple(sorted(set(left.permissions) - set(right.permissions))),
    )


def plan_joiner(employee: Employee, reason: str) -> LifecyclePlan:
    role = ROLE_BY_NAME.get(employee.job_role)
    if role is None or role.department != employee.department:
        raise LifecycleValidationError("Job role is not compatible with the selected department.")
    if employee.status != EmployeeStatus.ACTIVE:
        raise LifecycleValidationError("A new joiner must start with ACTIVE status.")
    after_access = expected_access(employee.job_role)
    return LifecyclePlan(
        operation="JOINER",
        employee_id=employee.employee_id,
        before_employee=None,
        after_employee=employee,
        before_access=EMPTY_ACCESS,
        after_access=after_access,
        to_remove=AccessChanges(),
        to_add=_changes(after_access, EMPTY_ACCESS),
        reason=reason.strip() or "New employee onboarding",
    )


def plan_mover(
    employee: Employee,
    current_access: EffectiveAccess,
    new_job_role: str,
    reason: str,
) -> LifecyclePlan:
    if employee.status != EmployeeStatus.ACTIVE:
        raise LifecycleValidationError("Only an active employee can be moved.")
    role = ROLE_BY_NAME.get(new_job_role)
    if role is None:
        raise LifecycleValidationError(f"Unknown job role: {new_job_role}")
    if employee.job_role == new_job_role:
        raise LifecycleValidationError("Select a different job role for the mover operation.")

    after_employee = replace(employee, department=role.department, job_role=role.name)
    after_access = expected_access(role.name)
    return LifecyclePlan(
        operation="MOVER",
        employee_id=employee.employee_id,
        before_employee=employee,
        after_employee=after_employee,
        before_access=current_access,
        after_access=after_access,
        to_remove=_changes(current_access, after_access),
        to_add=_changes(after_access, current_access),
        reason=reason.strip() or "Department or job-role change",
    )


def plan_leaver(
    employee: Employee,
    current_access: EffectiveAccess,
    reason: str,
) -> LifecyclePlan:
    if employee.status != EmployeeStatus.ACTIVE:
        raise LifecycleValidationError("The selected employee is already disabled.")
    after_employee = replace(employee, status=EmployeeStatus.DISABLED)
    return LifecyclePlan(
        operation="LEAVER",
        employee_id=employee.employee_id,
        before_employee=employee,
        after_employee=after_employee,
        before_access=current_access,
        after_access=EMPTY_ACCESS,
        to_remove=_changes(current_access, EMPTY_ACCESS),
        to_add=AccessChanges(),
        reason=reason.strip() or "Employee offboarding",
    )
