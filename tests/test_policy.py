from cilamp.domain import EffectiveAccess, Employee, EmployeeStatus, RiskLevel
from cilamp.policy import access_source_rows, evaluate_access, expected_access


def _employee(role: str = "Developer", department: str = "Engineering") -> Employee:
    return Employee(
        "CIL9001",
        "Policy Test",
        "policy.test@example.cilamp",
        department,
        role,
        EmployeeStatus.ACTIVE,
    )


def test_valid_role_access_is_compliant_and_explained_as_inherited() -> None:
    employee = _employee()
    review = evaluate_access(employee, expected_access(employee))

    assert review.compliant
    assert not review.privileged
    assert all(row["Policy"] == "EXPECTED" for row in access_source_rows(review))
    assert all("role/group policy" in row["Source"] for row in access_source_rows(review))


def test_developer_administrator_permission_is_critical_excess() -> None:
    employee = _employee()
    expected = expected_access(employee)
    actual = EffectiveAccess(
        expected.groups,
        expected.applications,
        (*expected.permissions, "platform.administrator"),
    )

    review = evaluate_access(employee, actual)
    finding = next(
        item for item in review.findings if item.entitlement == "platform.administrator"
    )

    assert finding.category == "EXCESSIVE_PRIVILEGE"
    assert finding.risk == RiskLevel.CRITICAL
    assert review.privileged
    assert review.privilege_creep


def test_missing_and_stale_access_are_distinguished() -> None:
    employee = _employee()
    expected = expected_access(employee)
    actual = EffectiveAccess(
        expected.groups,
        tuple(item for item in expected.applications if item != "GitHub"),
        (*expected.permissions, "finance.read"),
    )

    review = evaluate_access(employee, actual)
    findings = {(item.category, item.entitlement) for item in review.findings}

    assert ("MISSING_ACCESS", "GitHub") in findings
    assert ("PRIVILEGE_CREEP", "finance.read") in findings


def test_disabled_identity_expects_no_access() -> None:
    employee = _employee()
    disabled = Employee(
        employee.employee_id,
        employee.display_name,
        employee.email,
        employee.department,
        employee.job_role,
        EmployeeStatus.DISABLED,
    )

    assert expected_access(disabled) == EffectiveAccess((), (), ())
