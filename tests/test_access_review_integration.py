import sqlite3
from contextlib import closing
from pathlib import Path

import pytest

from cilamp.access_review_service import (
    create_developer_admin_scenario,
    remediate_employee,
    review_all,
    review_employee,
    review_summary,
)
from cilamp.repository import (
    LifecycleConflict,
    get_assigned_access,
    initialize_organization,
    list_audit_events,
)


TEST_DATA_DIR = Path(__file__).parents[1] / "data"


@pytest.fixture
def review_database():
    database_path = TEST_DATA_DIR / "test-access-review.db"
    database_path.unlink(missing_ok=True)
    initialize_organization(database_path)
    try:
        yield database_path
    finally:
        database_path.unlink(missing_ok=True)


def test_clean_organization_is_compliant_and_privileged_roles_are_identified(
    review_database: Path,
) -> None:
    reviews = review_all(review_database)
    summary = review_summary(reviews)

    assert summary["identities"] == 500
    assert summary["compliant"] == 500
    assert summary["findings"] == 0
    assert summary["privileged"] == 85
    assert review_employee(review_database, "CIL0001").privileged is False
    assert review_employee(review_database, "CIL0411").privileged is True


def test_excess_privilege_scenario_is_detected_audited_and_remediated(
    review_database: Path,
) -> None:
    employee_id = "CIL0001"
    scenario_correlation = create_developer_admin_scenario(review_database, employee_id)
    review = review_employee(review_database, employee_id)

    assert any(
        item.category == "EXCESSIVE_PRIVILEGE"
        and item.entitlement == "platform.administrator"
        for item in review.findings
    )
    assert "platform.administrator" in review.actual.permissions
    scenario_events = list_audit_events(review_database, target_identity=employee_id)
    assert any(
        event.action == "SIMULATION_VIOLATION_CREATED"
        and event.correlation_id == scenario_correlation
        for event in scenario_events
    )

    remediation_correlation = remediate_employee(review_database, review)
    remediated = review_employee(review_database, employee_id)
    remediation_events = list_audit_events(review_database, target_identity=employee_id)

    assert remediated.compliant
    assert "platform.administrator" not in get_assigned_access(
        review_database, employee_id
    ).permissions
    assert any(
        event.action == "ACCESS_REMEDIATED"
        and event.correlation_id == remediation_correlation
        for event in remediation_events
    )


def test_unauthorized_group_application_and_missing_access_are_detected(
    review_database: Path,
) -> None:
    employee_id = "CIL0001"
    with closing(sqlite3.connect(review_database)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO employee_groups VALUES (?, ?)",
                (employee_id, "Finance"),
            )
            connection.execute(
                "INSERT INTO employee_applications VALUES (?, ?)",
                (employee_id, "Finance Portal"),
            )
            connection.execute(
                "DELETE FROM employee_permissions WHERE employee_id = ? AND permission_name = ?",
                (employee_id, "source.read_write"),
            )

    review = review_employee(review_database, employee_id)
    findings = {(item.category, item.entitlement) for item in review.findings}

    assert ("UNAUTHORIZED_ACCESS", "Finance") in findings
    assert ("UNAUTHORIZED_ACCESS", "Finance Portal") in findings
    assert ("MISSING_ACCESS", "source.read_write") in findings


def test_remediation_rejects_stale_review(review_database: Path) -> None:
    employee_id = "CIL0001"
    create_developer_admin_scenario(review_database, employee_id)
    stale_review = review_employee(review_database, employee_id)
    with closing(sqlite3.connect(review_database)) as connection:
        with connection:
            connection.execute(
                "DELETE FROM employee_permissions WHERE employee_id = ? AND permission_name = ?",
                (employee_id, "platform.administrator"),
            )

    with pytest.raises(LifecycleConflict, match="changed after review"):
        remediate_employee(review_database, stale_review)
