import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from cilamp.domain import EffectiveAccess, EmployeeStatus
from cilamp.iam_catalog import ROLE_BY_NAME
from cilamp.lifecycle import LifecycleValidationError
from cilamp.lifecycle_service import execute, preview_joiner, preview_leaver, preview_mover
from cilamp.repository import (
    LifecycleConflict,
    get_assigned_access,
    get_employee,
    initialize_organization,
    lifecycle_counts,
    list_audit_events,
    organization_counts,
)


TEST_DATA_DIR = Path(__file__).parents[1] / "data"


@pytest.fixture
def lifecycle_database():
    database_path = TEST_DATA_DIR / "test-lifecycle.db"
    database_path.unlink(missing_ok=True)
    initialize_organization(database_path)
    try:
        yield database_path
    finally:
        database_path.unlink(missing_ok=True)


def test_joiner_receives_only_expected_access_and_audit(lifecycle_database: Path) -> None:
    plan = preview_joiner(
        lifecycle_database,
        "Jordan Example",
        "jordan.example@example.cilamp",
        "Developer",
        "Approved new hire",
    )

    correlation_id = execute(lifecycle_database, plan)
    employee = get_employee(lifecycle_database, plan.employee_id)
    access = get_assigned_access(lifecycle_database, plan.employee_id)
    events = list_audit_events(lifecycle_database, target_identity=plan.employee_id)

    assert employee is not None
    assert organization_counts(lifecycle_database)["employees"] == 501
    assert set(access.groups) == set(ROLE_BY_NAME["Developer"].groups)
    assert "GitHub" in access.applications
    assert "Finance Portal" not in access.applications
    assert "cloud.ops.scoped" not in access.permissions
    assert any(event.action == "IDENTITY_CREATED" for event in events)
    assert any(event.action == "JOINER_COMPLETED" for event in events)
    assert {event.correlation_id for event in events} == {correlation_id}


def test_mover_removes_old_and_excess_access_before_granting_new(
    lifecycle_database: Path,
) -> None:
    employee_id = "CIL0001"
    with closing(sqlite3.connect(lifecycle_database)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO employee_permissions VALUES (?, ?)",
                (employee_id, "cloud.ops.scoped"),
            )

    plan = preview_mover(
        lifecycle_database, employee_id, "Finance Analyst", "Approved transfer"
    )
    assert "cloud.ops.scoped" in plan.to_remove.permissions

    correlation_id = execute(lifecycle_database, plan)
    employee = get_employee(lifecycle_database, employee_id)
    access = get_assigned_access(lifecycle_database, employee_id)
    events = [
        event
        for event in reversed(list_audit_events(lifecycle_database, target_identity=employee_id))
        if event.correlation_id == correlation_id
    ]
    actions = [event.action for event in events]

    assert employee is not None
    assert employee.department == "Finance"
    assert employee.job_role == "Finance Analyst"
    assert set(access.groups) == set(ROLE_BY_NAME["Finance Analyst"].groups)
    assert set(access.applications) == set(ROLE_BY_NAME["Finance Analyst"].applications)
    assert set(access.permissions) == set(ROLE_BY_NAME["Finance Analyst"].permissions)
    assert "cloud.ops.scoped" not in access.permissions
    assert actions.index("PERMISSION_REVOKED") < actions.index("PERMISSION_GRANTED")
    assert actions[-1] == "MOVER_COMPLETED"


def test_leaver_is_disabled_revoke_all_access_and_preserve_audit(
    lifecycle_database: Path,
) -> None:
    employee_id = "CIL0002"
    plan = preview_leaver(lifecycle_database, employee_id, "Employment ended")

    execute(lifecycle_database, plan)
    employee = get_employee(lifecycle_database, employee_id)
    access = get_assigned_access(lifecycle_database, employee_id)
    actions = {
        event.action
        for event in list_audit_events(lifecycle_database, target_identity=employee_id)
    }

    assert employee is not None
    assert employee.status == EmployeeStatus.DISABLED
    assert access == EffectiveAccess((), (), ())
    assert "ACCOUNT_DISABLED" in actions
    assert "LEAVER_COMPLETED" in actions
    assert lifecycle_counts(lifecycle_database)["LEAVER"] == 1

    initialize_organization(lifecycle_database)
    assert get_assigned_access(lifecycle_database, employee_id) == EffectiveAccess((), (), ())


def test_duplicate_joiner_and_disabled_mover_are_rejected(
    lifecycle_database: Path,
) -> None:
    with pytest.raises(LifecycleValidationError, match="already belongs"):
        preview_joiner(
            lifecycle_database,
            "Duplicate Example",
            "aarav.anderson.0001@example.iamconcen",
            "Developer",
            "Duplicate",
        )

    leaver = preview_leaver(lifecycle_database, "CIL0003", "Employment ended")
    execute(lifecycle_database, leaver)
    with pytest.raises(LifecycleValidationError, match="active employee"):
        preview_mover(
            lifecycle_database, "CIL0003", "Finance Analyst", "Invalid transfer"
        )


def test_stale_mover_preview_is_rejected(lifecycle_database: Path) -> None:
    employee_id = "CIL0004"
    stale_plan = preview_mover(
        lifecycle_database, employee_id, "Finance Analyst", "First request"
    )
    newer_plan = preview_mover(
        lifecycle_database, employee_id, "Sales User", "Approved newer request"
    )
    execute(lifecycle_database, newer_plan)

    with pytest.raises(LifecycleConflict, match="changed after preview"):
        execute(lifecycle_database, stale_plan)
