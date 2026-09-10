"""SQLite initialization and health checks for local simulation state."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path


SCHEMA_VERSION = 7


@dataclass(frozen=True)
class DatabaseHealth:
    status: str
    schema_version: int | None
    employee_count: int
    message: str

    @property
    def healthy(self) -> bool:
        return self.status == "HEALTHY"


def initialize_database(path: Path) -> None:
    """Create the minimal Phase 0 schema idempotently."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS system_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    email TEXT NOT NULL DEFAULT '',
                    department TEXT NOT NULL,
                    job_role TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'DISABLED'))
                )
                """
            )
            columns = {
                row[1] for row in connection.execute("PRAGMA table_info(employees)")
            }
            if "email" not in columns:
                connection.execute(
                    "ALTER TABLE employees ADD COLUMN email TEXT NOT NULL DEFAULT ''"
                )
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_employees_email_unique
                ON employees(email) WHERE email <> ''
                """
            )
            connection.execute(
                "INSERT OR REPLACE INTO system_metadata(key, value) VALUES (?, ?)",
                ("schema_version", str(SCHEMA_VERSION)),
            )


def check_database(path: Path) -> DatabaseHealth:
    """Return a display-safe health result without exposing database contents."""

    try:
        initialize_database(path)
        with closing(sqlite3.connect(path)) as connection:
            schema_row = connection.execute(
                "SELECT value FROM system_metadata WHERE key = 'schema_version'"
            ).fetchone()
            employee_count = connection.execute(
                "SELECT COUNT(*) FROM employees"
            ).fetchone()[0]
            connection.execute("SELECT 1").fetchone()

        schema_version = int(schema_row[0]) if schema_row else None
        return DatabaseHealth(
            status="HEALTHY",
            schema_version=schema_version,
            employee_count=employee_count,
            message="SQLite is initialized and responding.",
        )
    except (OSError, sqlite3.Error, ValueError) as error:
        return DatabaseHealth(
            status="UNHEALTHY",
            schema_version=None,
            employee_count=0,
            message=f"Database check failed: {type(error).__name__}",
        )
