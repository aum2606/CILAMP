import pytest

from cilamp.domain import EffectiveAccess, Employee, EmployeeStatus, RiskLevel
from cilamp.security import SCENARIOS, build_scenario_plan, troubleshooting_steps


def _employee(role: str, department: str) -> Employee:
    return Employee(
        "CIL9990",
        "Security Scenario",
        "security.scenario@example.cilamp",
        department,
        role,
        EmployeeStatus.ACTIVE,
    )


def test_all_six_required_scenarios_are_defined() -> None:
    assert {item.scenario_type for item in SCENARIOS} == {
        "EXCESSIVE_PRIVILEGE",
        "OLD_DEPARTMENT_ACCESS",
        "DISABLED_WITH_APPLICATION",
        "UNAUTHORIZED_GROUP",
        "INSECURE_WORKLOAD_CREDENTIAL",
        "MISSING_REQUIRED_ACCESS",
    }


def test_excessive_privilege_plan_contains_no_real_secret() -> None:
    plan = build_scenario_plan(
        "EXCESSIVE_PRIVILEGE",
        _employee("Developer", "Engineering"),
        EffectiveAccess((), (), ()),
    )

    assert plan.risk == RiskLevel.CRITICAL
    assert plan.to_add.permissions == ("platform.administrator",)


def test_workload_scenario_stores_metadata_not_a_credential() -> None:
    plan = build_scenario_plan(
        "INSECURE_WORKLOAD_CREDENTIAL", None, EffectiveAccess((), (), ())
    )

    assert plan.target_identity.startswith("workload:")
    assert plan.evidence["secret_value_stored"] == "NO"
    assert set(plan.evidence) == {
        "identity_type",
        "credential_storage",
        "secret_value_stored",
    }


def test_missing_access_requires_application_to_be_present() -> None:
    employee = _employee("Developer", "Engineering")

    with pytest.raises(ValueError, match="already lacks GitHub"):
        build_scenario_plan(
            "MISSING_REQUIRED_ACCESS", employee, EffectiveAccess((), (), ())
        )


def test_every_scenario_has_actionable_troubleshooting_steps() -> None:
    from datetime import datetime, timezone

    from cilamp.domain import FindingStatus, SecurityFinding

    for scenario in SCENARIOS:
        finding = SecurityFinding(
            "finding",
            datetime.now(timezone.utc),
            "target",
            scenario.scenario_type,
            scenario.title,
            scenario.purpose,
            RiskLevel.HIGH,
            FindingStatus.OPEN,
            {},
            "recommendation",
            "correlation",
        )
        assert len(troubleshooting_steps(finding)) >= 6
