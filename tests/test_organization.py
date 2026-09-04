from cilamp.iam_catalog import ROLE_BY_NAME
from cilamp.organization import ROLE_COUNTS, generate_employees


def test_generator_creates_exactly_500_unique_valid_employees() -> None:
    employees = generate_employees()

    assert len(employees) == 500
    assert sum(ROLE_COUNTS.values()) == 500
    assert len({employee.employee_id for employee in employees}) == 500
    assert len({employee.email for employee in employees}) == 500
    assert all(
        ROLE_BY_NAME[employee.job_role].department == employee.department
        for employee in employees
    )
    assert all(employee.status.value == "ACTIVE" for employee in employees)


def test_generator_is_deterministic() -> None:
    assert generate_employees() == generate_employees()
