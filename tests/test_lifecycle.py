import pytest

from cilamp.domain import EffectiveAccess, Employee, EmployeeStatus
from cilamp.lifecycle import LifecycleValidationError, expected_access, plan_leaver, plan_mover


def _developer() -> Employee:
    return Employee(
        "CIL9000",
        "Test Developer",
        "test.developer@example.cilamp",
        "Engineering",
        "Developer",
        EmployeeStatus.ACTIVE,
    )


def test_mover_plan_removes_old_access_and_adds_new_access() -> None:
    employee = _developer()
    current = expected_access("Developer")

    plan = plan_mover(employee, current, "Finance Analyst", "Approved transfer")

    assert plan.after_employee.department == "Finance"
    assert "Developers" in plan.to_remove.groups
    assert "GitHub" in plan.to_remove.applications
    assert "source.read_write" in plan.to_remove.permissions
    assert "Finance" in plan.to_add.groups
    assert "Finance Portal" in plan.to_add.applications
    assert "finance.read" in plan.to_add.permissions
    assert "source.read_write" not in plan.after_access.permissions


def test_mover_rejects_same_role() -> None:
    employee = _developer()

    with pytest.raises(LifecycleValidationError, match="different job role"):
        plan_mover(employee, expected_access("Developer"), "Developer", "No change")


def test_leaver_plan_disables_identity_and_removes_all_access() -> None:
    employee = _developer()
    current = expected_access("Developer")

    plan = plan_leaver(employee, current, "Employment ended")

    assert plan.after_employee.status == EmployeeStatus.DISABLED
    assert plan.after_access == EffectiveAccess((), (), ())
    assert set(plan.to_remove.groups) == set(current.groups)
    assert set(plan.to_remove.applications) == set(current.applications)
    assert set(plan.to_remove.permissions) == set(current.permissions)
