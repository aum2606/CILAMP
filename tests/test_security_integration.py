from pathlib import Path

import pytest

from cilamp.domain import EffectiveAccess, EmployeeStatus, FindingStatus
from cilamp.repository import (
    audit_statistics,
    get_assigned_access,
    get_employee,
    initialize_organization,
    list_audit_events,
    list_security_findings,
)
from cilamp.security_service import (
    create_security_scenario,
    preview_security_scenario,
    remediate_security_finding,
)


TEST_DATA_DIR = Path(__file__).parents[1] / "data"


@pytest.fixture
def security_database():
    database_path = TEST_DATA_DIR / "test-security.db"
    database_path.unlink(missing_ok=True)
    initialize_organization(database_path)
    try:
        yield database_path
    finally:
        database_path.unlink(missing_ok=True)


SCENARIO_TARGETS = (
    ("EXCESSIVE_PRIVILEGE", "CIL0001"),
    ("OLD_DEPARTMENT_ACCESS", "CIL0151"),
    ("DISABLED_WITH_APPLICATION", "CIL0002"),
    ("UNAUTHORIZED_GROUP", "CIL0003"),
    ("INSECURE_WORKLOAD_CREDENTIAL", None),
    ("MISSING_REQUIRED_ACCESS", "CIL0004"),
)


def _create_all_scenarios(path: Path) -> None:
    for scenario_type, employee_id in SCENARIO_TARGETS:
        plan = preview_security_scenario(path, scenario_type, employee_id)
        create_security_scenario(path, plan)


def test_six_scenarios_create_open_findings_and_truthful_failed_checks(
    security_database: Path,
) -> None:
    _create_all_scenarios(security_database)

    findings = list_security_findings(security_database)
    statistics = audit_statistics(security_database)

    assert len(findings) == 6
    assert {finding.scenario_type for finding in findings} == {
        item[0] for item in SCENARIO_TARGETS
    }
    assert all(finding.status == FindingStatus.OPEN for finding in findings)
    assert statistics["open_findings"] == 6
    assert statistics["failed"] == 6
    failed_events = [
        event for event in list_audit_events(security_database, limit=1000)
        if event.result == "FAILURE"
    ]
    assert len(failed_events) == 6
    assert all("CHECK" in event.action or "REVIEW" in event.action for event in failed_events)


def test_scenarios_create_the_expected_security_state(security_database: Path) -> None:
    _create_all_scenarios(security_database)

    assert "platform.administrator" in get_assigned_access(
        security_database, "CIL0001"
    ).permissions
    finance_access = get_assigned_access(security_database, "CIL0151")
    assert "Developers" in finance_access.groups
    assert "GitHub" in finance_access.applications
    disabled = get_employee(security_database, "CIL0002")
    assert disabled is not None and disabled.status == EmployeeStatus.DISABLED
    assert get_assigned_access(security_database, "CIL0002") == EffectiveAccess(
        (), ("Internal Portal",), ()
    )
    assert "Finance" in get_assigned_access(security_database, "CIL0003").groups
    assert "GitHub" not in get_assigned_access(
        security_database, "CIL0004"
    ).applications
    workload = next(
        finding
        for finding in list_security_findings(security_database)
        if finding.scenario_type == "INSECURE_WORKLOAD_CREDENTIAL"
    )
    assert workload.evidence["secret_value_stored"] == "NO"


def test_all_scenarios_can_be_remediated_with_audit_evidence(
    security_database: Path,
) -> None:
    _create_all_scenarios(security_database)
    findings = list_security_findings(security_database, status="OPEN")

    for finding in findings:
        correlation_id, resolved_count = remediate_security_finding(
            security_database, finding.finding_id
        )
        assert resolved_count >= 1
        assert any(
            event.action == "SECURITY_FINDING_REMEDIATED"
            and event.correlation_id == correlation_id
            for event in list_audit_events(
                security_database, target_identity=finding.target_identity, limit=1000
            )
        )

    assert not list_security_findings(security_database, status="OPEN")
    assert len(list_security_findings(security_database, status="REMEDIATED")) == 6
    assert audit_statistics(security_database)["remediated_findings"] == 6
    assert get_assigned_access(security_database, "CIL0001").permissions.count(
        "platform.administrator"
    ) == 0
    disabled = get_employee(security_database, "CIL0002")
    assert disabled is not None and disabled.status == EmployeeStatus.DISABLED
    assert get_assigned_access(security_database, "CIL0002") == EffectiveAccess((), (), ())
    assert "GitHub" in get_assigned_access(security_database, "CIL0004").applications


def test_security_finding_filters_are_parameterized(security_database: Path) -> None:
    _create_all_scenarios(security_database)

    critical = list_security_findings(security_database, risk="CRITICAL")
    target = list_security_findings(security_database, target_identity="CIL0001")

    assert len(critical) == 2
    assert len(target) == 1
    assert target[0].scenario_type == "EXCESSIVE_PRIVILEGE"
