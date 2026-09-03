import sqlite3
from contextlib import closing
from pathlib import Path

from cilamp.database import SCHEMA_VERSION, check_database, initialize_database


TEST_DATA_DIR = Path(__file__).parents[1] / "data"


def _fresh_database(name: str) -> Path:
    database_path = TEST_DATA_DIR / name
    database_path.unlink(missing_ok=True)
    return database_path


def test_initialize_database_is_idempotent() -> None:
    database_path = _fresh_database("test-idempotent.db")

    try:
        initialize_database(database_path)
        initialize_database(database_path)

        with closing(sqlite3.connect(database_path)) as connection:
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
            }

        assert {"system_metadata", "employees"}.issubset(tables)
    finally:
        database_path.unlink(missing_ok=True)


def test_database_health_reports_schema_and_empty_employee_store() -> None:
    database_path = _fresh_database("test-health.db")

    try:
        result = check_database(database_path)

        assert result.healthy
        assert result.schema_version == SCHEMA_VERSION
        assert result.employee_count == 0
    finally:
        database_path.unlink(missing_ok=True)
