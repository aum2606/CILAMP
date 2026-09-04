from pathlib import Path

from cilamp.repository import (
    effective_access,
    initialize_organization,
    list_employees,
    organization_counts,
)


TEST_DATA_DIR = Path(__file__).parents[1] / "data"


def _fresh_database() -> Path:
    database_path = TEST_DATA_DIR / "test-organization.db"
    database_path.unlink(missing_ok=True)
    return database_path


def test_organization_seed_is_complete_and_idempotent() -> None:
    database_path = _fresh_database()
    try:
        initialize_organization(database_path)
        initialize_organization(database_path)
        counts = organization_counts(database_path)

        assert counts == {
            "employees": 500,
            "departments": 6,
            "roles": 10,
            "groups": 13,
            "applications": 10,
        }
    finally:
        database_path.unlink(missing_ok=True)


def test_employee_filters_and_effective_access() -> None:
    database_path = _fresh_database()
    try:
        initialize_organization(database_path)
        developers = list_employees(
            database_path, department="Engineering", job_role="Developer"
        )
        selected = developers[0]
        search_result = list_employees(database_path, search=selected.employee_id)
        access = effective_access(selected)

        assert len(developers) == 120
        assert search_result == [selected]
        assert "Developers" in access.groups
        assert "GitHub" in access.applications
        assert "finance.read" not in access.permissions
    finally:
        database_path.unlink(missing_ok=True)
