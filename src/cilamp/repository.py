"""SQLite persistence and queries for the Phase 1 organization model."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

from cilamp.database import initialize_database
from cilamp.domain import EffectiveAccess, Employee, EmployeeStatus
from cilamp.iam_catalog import APPLICATIONS, DEPARTMENTS, PERMISSIONS, ROLES, ROLE_BY_NAME
from cilamp.organization import generate_employees


def initialize_organization(path: Path) -> None:
    """Create catalog tables and seed fictional identities idempotently."""

    initialize_database(path)
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS departments (
                    name TEXT PRIMARY KEY
                );
                CREATE TABLE IF NOT EXISTS job_roles (
                    name TEXT PRIMARY KEY,
                    department TEXT NOT NULL REFERENCES departments(name),
                    privileged INTEGER NOT NULL CHECK (privileged IN (0, 1))
                );
                CREATE TABLE IF NOT EXISTS iam_groups (
                    name TEXT PRIMARY KEY
                );
                CREATE TABLE IF NOT EXISTS applications (
                    name TEXT PRIMARY KEY,
                    sensitivity TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS permissions (
                    name TEXT PRIMARY KEY,
                    description TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS role_groups (
                    role_name TEXT NOT NULL REFERENCES job_roles(name),
                    group_name TEXT NOT NULL REFERENCES iam_groups(name),
                    PRIMARY KEY (role_name, group_name)
                );
                CREATE TABLE IF NOT EXISTS role_applications (
                    role_name TEXT NOT NULL REFERENCES job_roles(name),
                    application_name TEXT NOT NULL REFERENCES applications(name),
                    PRIMARY KEY (role_name, application_name)
                );
                CREATE TABLE IF NOT EXISTS role_permissions (
                    role_name TEXT NOT NULL REFERENCES job_roles(name),
                    permission_name TEXT NOT NULL REFERENCES permissions(name),
                    PRIMARY KEY (role_name, permission_name)
                );
                """
            )
            connection.executemany(
                "INSERT OR IGNORE INTO departments(name) VALUES (?)",
                ((item.name,) for item in DEPARTMENTS),
            )
            connection.executemany(
                "INSERT OR IGNORE INTO applications(name, sensitivity) VALUES (?, ?)",
                ((item.name, item.sensitivity) for item in APPLICATIONS),
            )
            connection.executemany(
                "INSERT OR IGNORE INTO permissions(name, description) VALUES (?, ?)",
                ((item.name, item.description) for item in PERMISSIONS),
            )
            connection.executemany(
                "INSERT OR IGNORE INTO job_roles(name, department, privileged) VALUES (?, ?, ?)",
                ((role.name, role.department, int(role.privileged)) for role in ROLES),
            )
            connection.executemany(
                "INSERT OR IGNORE INTO iam_groups(name) VALUES (?)",
                ((group,) for role in ROLES for group in role.groups),
            )
            connection.executemany(
                "INSERT OR IGNORE INTO role_groups(role_name, group_name) VALUES (?, ?)",
                ((role.name, group) for role in ROLES for group in role.groups),
            )
            connection.executemany(
                "INSERT OR IGNORE INTO role_applications(role_name, application_name) VALUES (?, ?)",
                ((role.name, app) for role in ROLES for app in role.applications),
            )
            connection.executemany(
                "INSERT OR IGNORE INTO role_permissions(role_name, permission_name) VALUES (?, ?)",
                ((role.name, permission) for role in ROLES for permission in role.permissions),
            )

            employee_count = connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
            if employee_count == 0:
                connection.executemany(
                    """
                    INSERT INTO employees(
                        employee_id, display_name, email, department, job_role, status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        (
                            employee.employee_id,
                            employee.display_name,
                            employee.email,
                            employee.department,
                            employee.job_role,
                            employee.status.value,
                        )
                        for employee in generate_employees()
                    ),
                )


def list_employees(
    path: Path,
    search: str = "",
    department: str | None = None,
    job_role: str | None = None,
    status: str | None = None,
) -> list[Employee]:
    clauses: list[str] = []
    parameters: list[str] = []
    if search.strip():
        clauses.append("(employee_id LIKE ? OR display_name LIKE ? OR email LIKE ?)")
        pattern = f"%{search.strip()}%"
        parameters.extend((pattern, pattern, pattern))
    if department:
        clauses.append("department = ?")
        parameters.append(department)
    if job_role:
        clauses.append("job_role = ?")
        parameters.append(job_role)
    if status:
        clauses.append("status = ?")
        parameters.append(status)

    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    query = (
        "SELECT employee_id, display_name, email, department, job_role, status "
        f"FROM employees{where} ORDER BY employee_id"
    )
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [
        Employee(
            employee_id=row[0], display_name=row[1], email=row[2], department=row[3],
            job_role=row[4], status=EmployeeStatus(row[5]),
        )
        for row in rows
    ]


def get_employee(path: Path, employee_id: str) -> Employee | None:
    employees = list_employees(path, search=employee_id)
    return next((item for item in employees if item.employee_id == employee_id), None)


def effective_access(employee: Employee) -> EffectiveAccess:
    role = ROLE_BY_NAME[employee.job_role]
    return EffectiveAccess(role.groups, role.applications, role.permissions)


def organization_counts(path: Path) -> dict[str, int]:
    with closing(sqlite3.connect(path)) as connection:
        return {
            "employees": connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0],
            "departments": connection.execute("SELECT COUNT(*) FROM departments").fetchone()[0],
            "roles": connection.execute("SELECT COUNT(*) FROM job_roles").fetchone()[0],
            "groups": connection.execute("SELECT COUNT(*) FROM iam_groups").fetchone()[0],
            "applications": connection.execute("SELECT COUNT(*) FROM applications").fetchone()[0],
        }


def distribution(path: Path, column: str) -> list[dict[str, int | str]]:
    allowed_columns = {"department", "job_role", "status"}
    if column not in allowed_columns:
        raise ValueError(f"Unsupported distribution column: {column}")
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            f"SELECT {column}, COUNT(*) FROM employees GROUP BY {column} ORDER BY {column}"
        ).fetchall()
    return [{column: row[0], "Employees": row[1]} for row in rows]
