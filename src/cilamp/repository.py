"""SQLite persistence for organization, access assignments, and lifecycle audit."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from cilamp.database import initialize_database
from cilamp.domain import (
    AuditEvent,
    EffectiveAccess,
    Employee,
    EmployeeStatus,
    FindingStatus,
    LifecyclePlan,
    RiskLevel,
    SecurityFinding,
    SecurityScenarioPlan,
)
from cilamp.iam_catalog import APPLICATIONS, DEPARTMENTS, PERMISSIONS, ROLES, ROLE_BY_NAME
from cilamp.organization import generate_employees


class LifecycleConflict(RuntimeError):
    """Raised when persisted identity state changed after a lifecycle preview."""


def initialize_organization(path: Path) -> None:
    """Create the local IAM schema and seed identities/access exactly once."""

    initialize_database(path)
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
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
                CREATE TABLE IF NOT EXISTS employee_groups (
                    employee_id TEXT NOT NULL REFERENCES employees(employee_id),
                    group_name TEXT NOT NULL REFERENCES iam_groups(name),
                    PRIMARY KEY (employee_id, group_name)
                );
                CREATE TABLE IF NOT EXISTS employee_applications (
                    employee_id TEXT NOT NULL REFERENCES employees(employee_id),
                    application_name TEXT NOT NULL REFERENCES applications(name),
                    PRIMARY KEY (employee_id, application_name)
                );
                CREATE TABLE IF NOT EXISTS employee_permissions (
                    employee_id TEXT NOT NULL REFERENCES employees(employee_id),
                    permission_name TEXT NOT NULL REFERENCES permissions(name),
                    PRIMARY KEY (employee_id, permission_name)
                );
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    target_identity TEXT NOT NULL,
                    action TEXT NOT NULL,
                    old_state TEXT NOT NULL,
                    new_state TEXT NOT NULL,
                    result TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    correlation_id TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_audit_target
                    ON audit_events(target_identity, timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_audit_correlation
                    ON audit_events(correlation_id);
                CREATE TABLE IF NOT EXISTS security_findings (
                    finding_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    target_identity TEXT NOT NULL,
                    scenario_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    risk TEXT NOT NULL,
                    status TEXT NOT NULL CHECK (status IN ('OPEN', 'REMEDIATED')),
                    evidence TEXT NOT NULL,
                    recommendation TEXT NOT NULL,
                    correlation_id TEXT NOT NULL,
                    resolved_at TEXT,
                    resolution TEXT NOT NULL DEFAULT ''
                );
                CREATE INDEX IF NOT EXISTS idx_findings_status
                    ON security_findings(status, risk, created_at DESC);
                CREATE INDEX IF NOT EXISTS idx_findings_target
                    ON security_findings(target_identity, created_at DESC);
                """
            )
            _seed_catalog(connection)
            employee_count = connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
            if employee_count == 0:
                _insert_employees(connection, generate_employees())

            access_seeded = connection.execute(
                "SELECT value FROM system_metadata WHERE key = 'actual_access_seeded'"
            ).fetchone()
            if access_seeded is None:
                rows = connection.execute("SELECT employee_id, job_role FROM employees").fetchall()
                for employee_id, job_role in rows:
                    role = ROLE_BY_NAME.get(job_role)
                    if role:
                        _grant_access(
                            connection,
                            employee_id,
                            EffectiveAccess(role.groups, role.applications, role.permissions),
                        )
                connection.execute(
                    "INSERT INTO system_metadata(key, value) VALUES (?, ?)",
                    ("actual_access_seeded", "true"),
                )


def _seed_catalog(connection: sqlite3.Connection) -> None:
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


def _insert_employees(connection: sqlite3.Connection, employees) -> None:
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
            for employee in employees
        ),
    )


def _grant_access(
    connection: sqlite3.Connection, employee_id: str, access: EffectiveAccess
) -> None:
    connection.executemany(
        "INSERT OR IGNORE INTO employee_groups VALUES (?, ?)",
        ((employee_id, item) for item in access.groups),
    )
    connection.executemany(
        "INSERT OR IGNORE INTO employee_applications VALUES (?, ?)",
        ((employee_id, item) for item in access.applications),
    )
    connection.executemany(
        "INSERT OR IGNORE INTO employee_permissions VALUES (?, ?)",
        ((employee_id, item) for item in access.permissions),
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
    return [_employee_from_row(row) for row in rows]


def _employee_from_row(row) -> Employee:
    return Employee(
        employee_id=row[0],
        display_name=row[1],
        email=row[2],
        department=row[3],
        job_role=row[4],
        status=EmployeeStatus(row[5]),
    )


def get_employee(path: Path, employee_id: str) -> Employee | None:
    with closing(sqlite3.connect(path)) as connection:
        row = connection.execute(
            """
            SELECT employee_id, display_name, email, department, job_role, status
            FROM employees WHERE employee_id = ?
            """,
            (employee_id,),
        ).fetchone()
    return _employee_from_row(row) if row else None


def effective_access(employee: Employee) -> EffectiveAccess:
    """Return expected access from the role catalog."""

    role = ROLE_BY_NAME[employee.job_role]
    return EffectiveAccess(role.groups, role.applications, role.permissions)


def get_assigned_access(path: Path, employee_id: str) -> EffectiveAccess:
    """Return the employee's actual persisted assignments."""

    with closing(sqlite3.connect(path)) as connection:
        groups = connection.execute(
            "SELECT group_name FROM employee_groups WHERE employee_id = ? ORDER BY group_name",
            (employee_id,),
        ).fetchall()
        applications = connection.execute(
            """
            SELECT application_name FROM employee_applications
            WHERE employee_id = ? ORDER BY application_name
            """,
            (employee_id,),
        ).fetchall()
        permissions = connection.execute(
            """
            SELECT permission_name FROM employee_permissions
            WHERE employee_id = ? ORDER BY permission_name
            """,
            (employee_id,),
        ).fetchall()
    return EffectiveAccess(
        tuple(row[0] for row in groups),
        tuple(row[0] for row in applications),
        tuple(row[0] for row in permissions),
    )


def email_exists(path: Path, email: str) -> bool:
    with closing(sqlite3.connect(path)) as connection:
        return connection.execute(
            "SELECT 1 FROM employees WHERE lower(email) = lower(?)", (email,)
        ).fetchone() is not None


def next_employee_id(path: Path) -> str:
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT employee_id FROM employees WHERE employee_id GLOB 'CIL[0-9]*'"
        ).fetchall()
    numbers = [int(row[0][3:]) for row in rows if row[0][3:].isdigit()]
    return f"CIL{max(numbers, default=0) + 1:04d}"


def organization_counts(path: Path) -> dict[str, int]:
    with closing(sqlite3.connect(path)) as connection:
        return {
            "employees": connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0],
            "active": connection.execute(
                "SELECT COUNT(*) FROM employees WHERE status = 'ACTIVE'"
            ).fetchone()[0],
            "disabled": connection.execute(
                "SELECT COUNT(*) FROM employees WHERE status = 'DISABLED'"
            ).fetchone()[0],
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


def execute_lifecycle_plan(path: Path, plan: LifecyclePlan, actor: str) -> str:
    """Apply a confirmed plan atomically and audit each security-relevant step."""

    correlation_id = str(uuid4())
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            if plan.operation == "JOINER":
                _execute_joiner(connection, plan, actor, correlation_id)
            else:
                row = connection.execute(
                    """
                    SELECT employee_id, display_name, email, department, job_role, status
                    FROM employees WHERE employee_id = ?
                    """,
                    (plan.employee_id,),
                ).fetchone()
                current_employee = _employee_from_row(row) if row else None
                current_access = _assigned_access_from_connection(connection, plan.employee_id)
                if current_employee != plan.before_employee or current_access != plan.before_access:
                    raise LifecycleConflict(
                        "Identity state changed after preview. Generate a new lifecycle preview."
                    )
                if plan.operation == "MOVER":
                    _execute_mover(connection, plan, actor, correlation_id)
                elif plan.operation == "LEAVER":
                    _execute_leaver(connection, plan, actor, correlation_id)
                else:
                    raise ValueError(f"Unsupported lifecycle operation: {plan.operation}")
    return correlation_id


def _execute_joiner(connection, plan, actor: str, correlation_id: str) -> None:
    duplicate = connection.execute(
        "SELECT 1 FROM employees WHERE employee_id = ? OR lower(email) = lower(?)",
        (plan.employee_id, plan.after_employee.email),
    ).fetchone()
    if duplicate:
        raise LifecycleConflict("Joiner identity already exists. Generate a new preview.")
    _insert_employees(connection, (plan.after_employee,))
    _audit(connection, plan, actor, correlation_id, "IDENTITY_CREATED", "null", _json_employee(plan.after_employee))
    _grant_changes_with_audit(connection, plan, actor, correlation_id)
    _audit_summary(connection, plan, actor, correlation_id)


def _execute_mover(connection, plan, actor: str, correlation_id: str) -> None:
    _revoke_changes_with_audit(connection, plan, actor, correlation_id)
    connection.execute(
        "UPDATE employees SET department = ?, job_role = ? WHERE employee_id = ?",
        (plan.after_employee.department, plan.after_employee.job_role, plan.employee_id),
    )
    _audit(
        connection, plan, actor, correlation_id, "IDENTITY_UPDATED",
        _json_employee(plan.before_employee), _json_employee(plan.after_employee),
    )
    _grant_changes_with_audit(connection, plan, actor, correlation_id)
    _audit_summary(connection, plan, actor, correlation_id)


def _execute_leaver(connection, plan, actor: str, correlation_id: str) -> None:
    connection.execute(
        "UPDATE employees SET status = 'DISABLED' WHERE employee_id = ?",
        (plan.employee_id,),
    )
    _audit(
        connection, plan, actor, correlation_id, "ACCOUNT_DISABLED",
        plan.before_employee.status.value, EmployeeStatus.DISABLED.value,
    )
    _revoke_changes_with_audit(connection, plan, actor, correlation_id)
    _audit_summary(connection, plan, actor, correlation_id)


def _revoke_changes_with_audit(connection, plan, actor: str, correlation_id: str) -> None:
    mappings = (
        ("permissions", "employee_permissions", "permission_name", "PERMISSION_REVOKED"),
        ("groups", "employee_groups", "group_name", "GROUP_REVOKED"),
        ("applications", "employee_applications", "application_name", "APPLICATION_REVOKED"),
    )
    for field, table, column, action in mappings:
        for value in getattr(plan.to_remove, field):
            connection.execute(
                f"DELETE FROM {table} WHERE employee_id = ? AND {column} = ?",
                (plan.employee_id, value),
            )
            _audit(connection, plan, actor, correlation_id, action, value, "null")


def _grant_changes_with_audit(connection, plan, actor: str, correlation_id: str) -> None:
    mappings = (
        ("groups", "employee_groups", "group_name", "GROUP_GRANTED"),
        ("applications", "employee_applications", "application_name", "APPLICATION_GRANTED"),
        ("permissions", "employee_permissions", "permission_name", "PERMISSION_GRANTED"),
    )
    for field, table, column, action in mappings:
        for value in getattr(plan.to_add, field):
            connection.execute(
                f"INSERT INTO {table}(employee_id, {column}) VALUES (?, ?)",
                (plan.employee_id, value),
            )
            _audit(connection, plan, actor, correlation_id, action, "null", value)


def _assigned_access_from_connection(connection, employee_id: str) -> EffectiveAccess:
    def values(table: str, column: str) -> tuple[str, ...]:
        rows = connection.execute(
            f"SELECT {column} FROM {table} WHERE employee_id = ? ORDER BY {column}",
            (employee_id,),
        ).fetchall()
        return tuple(row[0] for row in rows)

    return EffectiveAccess(
        values("employee_groups", "group_name"),
        values("employee_applications", "application_name"),
        values("employee_permissions", "permission_name"),
    )


def _json_employee(employee: Employee | None) -> str:
    if employee is None:
        return "null"
    state = asdict(employee)
    state["status"] = employee.status.value
    return json.dumps(state, sort_keys=True)


def _json_access(access: EffectiveAccess) -> str:
    return json.dumps(asdict(access), sort_keys=True)


def _audit(connection, plan, actor, correlation_id, action, old_state, new_state) -> None:
    _write_audit_event(
        connection=connection,
        actor=actor,
        target_identity=plan.employee_id,
        action=action,
        old_state=old_state,
        new_state=new_state,
        reason=plan.reason,
        correlation_id=correlation_id,
    )


def _write_audit_event(
    connection: sqlite3.Connection,
    actor: str,
    target_identity: str,
    action: str,
    old_state: str,
    new_state: str,
    reason: str,
    correlation_id: str,
    result: str = "SUCCESS",
) -> None:
    connection.execute(
        "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            str(uuid4()),
            datetime.now(timezone.utc).isoformat(),
            actor,
            target_identity,
            action,
            old_state,
            new_state,
            result,
            reason,
            correlation_id,
        ),
    )


def _audit_summary(connection, plan, actor: str, correlation_id: str) -> None:
    _audit(
        connection,
        plan,
        actor,
        correlation_id,
        f"{plan.operation}_COMPLETED",
        _json_access(plan.before_access),
        _json_access(plan.after_access),
    )


def list_audit_events(
    path: Path, limit: int = 100, target_identity: str | None = None
) -> list[AuditEvent]:
    query = (
        "SELECT event_id, timestamp, actor, target_identity, action, old_state, "
        "new_state, result, reason, correlation_id FROM audit_events"
    )
    parameters: list[str | int] = []
    if target_identity:
        query += " WHERE target_identity = ?"
        parameters.append(target_identity)
    query += " ORDER BY timestamp DESC, rowid DESC LIMIT ?"
    parameters.append(max(1, min(limit, 1000)))
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(query, parameters).fetchall()
    return [
        AuditEvent(
            event_id=row[0],
            timestamp=datetime.fromisoformat(row[1]),
            actor=row[2],
            target_identity=row[3],
            action=row[4],
            old_state=row[5],
            new_state=row[6],
            result=row[7],
            reason=row[8],
            correlation_id=row[9],
        )
        for row in rows
    ]


def lifecycle_counts(path: Path) -> dict[str, int]:
    with closing(sqlite3.connect(path)) as connection:
        return {
            operation: connection.execute(
                "SELECT COUNT(*) FROM audit_events WHERE action = ?",
                (f"{operation}_COMPLETED",),
            ).fetchone()[0]
            for operation in ("JOINER", "MOVER", "LEAVER")
        }


def add_simulated_permission(
    path: Path,
    employee_id: str,
    permission: str,
    actor: str,
    reason: str,
) -> str:
    """Create an explicit, audited policy-violation scenario."""

    correlation_id = str(uuid4())
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            employee = connection.execute(
                "SELECT status FROM employees WHERE employee_id = ?", (employee_id,)
            ).fetchone()
            if employee is None:
                raise LifecycleConflict("Employee does not exist.")
            if employee[0] != EmployeeStatus.ACTIVE.value:
                raise LifecycleConflict("Cannot create a scenario for a disabled employee.")
            exists = connection.execute(
                """
                SELECT 1 FROM employee_permissions
                WHERE employee_id = ? AND permission_name = ?
                """,
                (employee_id, permission),
            ).fetchone()
            if exists:
                raise LifecycleConflict("The simulated permission is already assigned.")
            connection.execute(
                "INSERT INTO employee_permissions VALUES (?, ?)",
                (employee_id, permission),
            )
            _write_audit_event(
                connection,
                actor,
                employee_id,
                "SIMULATION_VIOLATION_CREATED",
                "null",
                permission,
                reason,
                correlation_id,
            )
    return correlation_id


def reconcile_access(
    path: Path,
    employee_id: str,
    before: EffectiveAccess,
    desired: EffectiveAccess,
    actor: str,
    reason: str,
) -> str:
    """Reconcile actual assignments to approved policy in one transaction."""

    correlation_id = str(uuid4())
    mappings = (
        ("groups", "employee_groups", "group_name"),
        ("applications", "employee_applications", "application_name"),
        ("permissions", "employee_permissions", "permission_name"),
    )
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            current = _assigned_access_from_connection(connection, employee_id)
            if current != before:
                raise LifecycleConflict(
                    "Access changed after review. Refresh the finding before remediation."
                )
            for field, table, column in mappings:
                current_values = set(getattr(before, field))
                desired_values = set(getattr(desired, field))
                for value in sorted(current_values - desired_values):
                    connection.execute(
                        f"DELETE FROM {table} WHERE employee_id = ? AND {column} = ?",
                        (employee_id, value),
                    )
                    _write_audit_event(
                        connection,
                        actor,
                        employee_id,
                        f"REMEDIATION_{field[:-1].upper()}_REMOVED",
                        value,
                        "null",
                        reason,
                        correlation_id,
                    )
                for value in sorted(desired_values - current_values):
                    connection.execute(
                        f"INSERT INTO {table}(employee_id, {column}) VALUES (?, ?)",
                        (employee_id, value),
                    )
                    _write_audit_event(
                        connection,
                        actor,
                        employee_id,
                        f"REMEDIATION_{field[:-1].upper()}_RESTORED",
                        "null",
                        value,
                        reason,
                        correlation_id,
                    )
            _write_audit_event(
                connection,
                actor,
                employee_id,
                "ACCESS_REMEDIATED",
                _json_access(before),
                _json_access(desired),
                reason,
                correlation_id,
            )
    return correlation_id


def execute_security_scenario(
    path: Path,
    plan: SecurityScenarioPlan,
    actor: str = "simulation.security-analyst",
) -> tuple[str, str]:
    """Apply a controlled scenario and persist its finding plus audit evidence."""

    correlation_id = str(uuid4())
    finding_id = str(uuid4())
    with closing(sqlite3.connect(path)) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        with connection:
            duplicate = connection.execute(
                """
                SELECT 1 FROM security_findings
                WHERE target_identity = ? AND scenario_type = ? AND status = 'OPEN'
                """,
                (plan.target_identity, plan.scenario_type),
            ).fetchone()
            if duplicate:
                raise LifecycleConflict(
                    "An open finding for this scenario and target already exists."
                )

            if not plan.target_identity.startswith("workload:"):
                employee = connection.execute(
                    "SELECT 1 FROM employees WHERE employee_id = ?",
                    (plan.target_identity,),
                ).fetchone()
                if employee is None:
                    raise LifecycleConflict("Scenario target employee does not exist.")
                _apply_scenario_access(connection, plan, actor, correlation_id)

            now = datetime.now(timezone.utc).isoformat()
            connection.execute(
                """
                INSERT INTO security_findings(
                    finding_id, created_at, target_identity, scenario_type, title,
                    description, risk, status, evidence, recommendation, correlation_id,
                    resolved_at, resolution
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN', ?, ?, ?, NULL, '')
                """,
                (
                    finding_id,
                    now,
                    plan.target_identity,
                    plan.scenario_type,
                    plan.title,
                    plan.description,
                    plan.risk.value,
                    json.dumps(plan.evidence, sort_keys=True),
                    plan.recommendation,
                    correlation_id,
                ),
            )
            _write_audit_event(
                connection,
                actor,
                plan.target_identity,
                plan.observed_action,
                "EXPECTED_CONTROL_STATE",
                json.dumps(plan.evidence, sort_keys=True),
                plan.description,
                correlation_id,
                result=plan.observed_result,
            )
            _write_audit_event(
                connection,
                actor,
                plan.target_identity,
                "SECURITY_FINDING_CREATED",
                "null",
                finding_id,
                plan.description,
                correlation_id,
            )
    return finding_id, correlation_id


def _apply_scenario_access(
    connection: sqlite3.Connection,
    plan: SecurityScenarioPlan,
    actor: str,
    correlation_id: str,
) -> None:
    mappings = (
        ("groups", "employee_groups", "group_name"),
        ("applications", "employee_applications", "application_name"),
        ("permissions", "employee_permissions", "permission_name"),
    )
    for field, table, column in mappings:
        for value in getattr(plan.to_remove, field):
            connection.execute(
                f"DELETE FROM {table} WHERE employee_id = ? AND {column} = ?",
                (plan.target_identity, value),
            )
            _write_audit_event(
                connection,
                actor,
                plan.target_identity,
                f"SCENARIO_{field[:-1].upper()}_REMOVED",
                value,
                "null",
                plan.description,
                correlation_id,
            )
    if plan.new_status is not None:
        old_status = connection.execute(
            "SELECT status FROM employees WHERE employee_id = ?",
            (plan.target_identity,),
        ).fetchone()[0]
        connection.execute(
            "UPDATE employees SET status = ? WHERE employee_id = ?",
            (plan.new_status.value, plan.target_identity),
        )
        _write_audit_event(
            connection,
            actor,
            plan.target_identity,
            "SCENARIO_STATUS_CHANGED",
            old_status,
            plan.new_status.value,
            plan.description,
            correlation_id,
        )
    for field, table, column in mappings:
        for value in getattr(plan.to_add, field):
            exists = connection.execute(
                f"SELECT 1 FROM {table} WHERE employee_id = ? AND {column} = ?",
                (plan.target_identity, value),
            ).fetchone()
            if exists:
                raise LifecycleConflict(
                    f"Scenario assignment already exists: {field[:-1]} {value}."
                )
            connection.execute(
                f"INSERT INTO {table}(employee_id, {column}) VALUES (?, ?)",
                (plan.target_identity, value),
            )
            _write_audit_event(
                connection,
                actor,
                plan.target_identity,
                f"SCENARIO_{field[:-1].upper()}_ADDED",
                "null",
                value,
                plan.description,
                correlation_id,
            )


def list_security_findings(
    path: Path,
    status: str | None = None,
    risk: str | None = None,
    scenario_type: str | None = None,
    target_identity: str | None = None,
) -> list[SecurityFinding]:
    clauses: list[str] = []
    parameters: list[str] = []
    for column, value in (
        ("status", status),
        ("risk", risk),
        ("scenario_type", scenario_type),
        ("target_identity", target_identity),
    ):
        if value:
            clauses.append(f"{column} = ?")
            parameters.append(value)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            """
            SELECT finding_id, created_at, target_identity, scenario_type, title,
                   description, risk, status, evidence, recommendation, correlation_id,
                   resolved_at, resolution
            FROM security_findings
            """
            + where
            + " ORDER BY created_at DESC, rowid DESC",
            parameters,
        ).fetchall()
    return [
        SecurityFinding(
            finding_id=row[0],
            created_at=datetime.fromisoformat(row[1]),
            target_identity=row[2],
            scenario_type=row[3],
            title=row[4],
            description=row[5],
            risk=RiskLevel(row[6]),
            status=FindingStatus(row[7]),
            evidence=json.loads(row[8]),
            recommendation=row[9],
            correlation_id=row[10],
            resolved_at=datetime.fromisoformat(row[11]) if row[11] else None,
            resolution=row[12],
        )
        for row in rows
    ]


def resolve_security_findings(
    path: Path,
    target_identity: str,
    actor: str,
    resolution: str,
    correlation_id: str,
) -> int:
    """Close all open findings for a reconciled target and audit the case action."""

    resolved_at = datetime.now(timezone.utc).isoformat()
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            finding_ids = [
                row[0]
                for row in connection.execute(
                    """
                    SELECT finding_id FROM security_findings
                    WHERE target_identity = ? AND status = 'OPEN'
                    """,
                    (target_identity,),
                ).fetchall()
            ]
            connection.execute(
                """
                UPDATE security_findings
                SET status = 'REMEDIATED', resolved_at = ?, resolution = ?
                WHERE target_identity = ? AND status = 'OPEN'
                """,
                (resolved_at, resolution, target_identity),
            )
            for finding_id in finding_ids:
                _write_audit_event(
                    connection,
                    actor,
                    target_identity,
                    "SECURITY_FINDING_REMEDIATED",
                    finding_id,
                    FindingStatus.REMEDIATED.value,
                    resolution,
                    correlation_id,
                )
    return len(finding_ids)


def audit_statistics(path: Path) -> dict[str, int]:
    with closing(sqlite3.connect(path)) as connection:
        return {
            "events": connection.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0],
            "failed": connection.execute(
                "SELECT COUNT(*) FROM audit_events WHERE result = 'FAILURE'"
            ).fetchone()[0],
            "open_findings": connection.execute(
                "SELECT COUNT(*) FROM security_findings WHERE status = 'OPEN'"
            ).fetchone()[0],
            "remediated_findings": connection.execute(
                "SELECT COUNT(*) FROM security_findings WHERE status = 'REMEDIATED'"
            ).fetchone()[0],
        }
