"""SQLite cache and local operation history for the Microsoft Entra connector."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from cilamp.connectors.entra.models import (
    EntraDirectoryAudit,
    EntraGroup,
    EntraOperation,
    EntraServicePrincipal,
    EntraSnapshot,
    EntraSyncState,
    EntraUser,
)


def initialize_entra_store(path: Path) -> None:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS entra_sync_state (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    status TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    tenant_label TEXT NOT NULL,
                    last_synced_at TEXT,
                    user_count INTEGER NOT NULL DEFAULT 0,
                    group_count INTEGER NOT NULL DEFAULT 0,
                    service_principal_count INTEGER NOT NULL DEFAULT 0,
                    audit_count INTEGER NOT NULL DEFAULT 0,
                    limitations TEXT NOT NULL DEFAULT '[]'
                );
                CREATE TABLE IF NOT EXISTS entra_users (
                    object_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    user_principal_name TEXT NOT NULL,
                    account_enabled INTEGER NOT NULL,
                    department TEXT NOT NULL,
                    job_title TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS entra_groups (
                    object_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    security_enabled INTEGER NOT NULL,
                    group_type TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS entra_service_principals (
                    object_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    application_id TEXT NOT NULL,
                    principal_type TEXT NOT NULL,
                    account_enabled INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS entra_group_memberships (
                    group_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    PRIMARY KEY (group_id, user_id)
                );
                CREATE TABLE IF NOT EXISTS entra_directory_audits (
                    record_id TEXT PRIMARY KEY,
                    activity_at TEXT NOT NULL,
                    activity TEXT NOT NULL,
                    result TEXT NOT NULL,
                    initiated_by TEXT NOT NULL,
                    target TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS entra_operations (
                    operation_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target TEXT NOT NULL,
                    result TEXT NOT NULL,
                    details TEXT NOT NULL,
                    correlation_id TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_entra_operations_time
                    ON entra_operations(timestamp DESC);
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO entra_sync_state(
                    singleton, status, mode, tenant_label
                ) VALUES (1, 'NOT_SYNCED', 'SIMULATION', 'Simulation tenant')
                """
            )


def save_entra_snapshot(
    path: Path, snapshot: EntraSnapshot, mode: str, tenant_label: str
) -> datetime:
    synced_at = datetime.now(timezone.utc)
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            for table in (
                "entra_users",
                "entra_groups",
                "entra_service_principals",
                "entra_group_memberships",
                "entra_directory_audits",
            ):
                connection.execute(f"DELETE FROM {table}")
            connection.executemany(
                "INSERT INTO entra_users VALUES (?, ?, ?, ?, ?, ?)",
                (
                    (
                        item.object_id,
                        item.display_name,
                        item.user_principal_name,
                        int(item.account_enabled),
                        item.department,
                        item.job_title,
                    )
                    for item in snapshot.users
                ),
            )
            connection.executemany(
                "INSERT INTO entra_groups VALUES (?, ?, ?, ?, ?)",
                (
                    (
                        item.object_id,
                        item.display_name,
                        item.description,
                        int(item.security_enabled),
                        item.group_type,
                    )
                    for item in snapshot.groups
                ),
            )
            connection.executemany(
                "INSERT INTO entra_service_principals VALUES (?, ?, ?, ?, ?)",
                (
                    (
                        item.object_id,
                        item.display_name,
                        item.application_id,
                        item.principal_type,
                        int(item.account_enabled),
                    )
                    for item in snapshot.service_principals
                ),
            )
            connection.executemany(
                "INSERT INTO entra_directory_audits VALUES (?, ?, ?, ?, ?, ?)",
                (
                    (
                        item.record_id,
                        item.activity_at.isoformat(),
                        item.activity,
                        item.result,
                        item.initiated_by,
                        item.target,
                    )
                    for item in snapshot.directory_audits
                ),
            )
            connection.execute(
                """
                UPDATE entra_sync_state SET
                    status = 'CONNECTED', mode = ?, tenant_label = ?,
                    last_synced_at = ?, user_count = ?, group_count = ?,
                    service_principal_count = ?, audit_count = ?, limitations = ?
                WHERE singleton = 1
                """,
                (
                    mode,
                    tenant_label,
                    synced_at.isoformat(),
                    len(snapshot.users),
                    len(snapshot.groups),
                    len(snapshot.service_principals),
                    len(snapshot.directory_audits),
                    json.dumps(snapshot.limitations),
                ),
            )
    return synced_at


def mark_entra_connection_failure(
    path: Path, mode: str, tenant_label: str, limitation: str
) -> None:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute(
                """
                UPDATE entra_sync_state
                SET status = 'ERROR', mode = ?, tenant_label = ?, limitations = ?
                WHERE singleton = 1
                """,
                (mode, tenant_label, json.dumps((limitation,))),
            )


def get_entra_sync_state(path: Path) -> EntraSyncState:
    with closing(sqlite3.connect(path)) as connection:
        row = connection.execute(
            """
            SELECT status, mode, tenant_label, last_synced_at, user_count,
                   group_count, service_principal_count, audit_count, limitations
            FROM entra_sync_state WHERE singleton = 1
            """
        ).fetchone()
    return EntraSyncState(
        row[0],
        row[1],
        row[2],
        datetime.fromisoformat(row[3]) if row[3] else None,
        row[4],
        row[5],
        row[6],
        row[7],
        tuple(json.loads(row[8])),
    )


def list_entra_users(path: Path) -> list[EntraUser]:
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM entra_users ORDER BY display_name"
        ).fetchall()
    return [EntraUser(row[0], row[1], row[2], bool(row[3]), row[4], row[5]) for row in rows]


def list_entra_groups(path: Path) -> list[EntraGroup]:
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM entra_groups ORDER BY display_name"
        ).fetchall()
    return [EntraGroup(row[0], row[1], row[2], bool(row[3]), row[4]) for row in rows]


def list_entra_service_principals(path: Path) -> list[EntraServicePrincipal]:
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM entra_service_principals ORDER BY display_name"
        ).fetchall()
    return [
        EntraServicePrincipal(row[0], row[1], row[2], row[3], bool(row[4]))
        for row in rows
    ]


def list_entra_directory_audits(path: Path) -> list[EntraDirectoryAudit]:
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM entra_directory_audits ORDER BY activity_at DESC"
        ).fetchall()
    return [
        EntraDirectoryAudit(
            row[0], datetime.fromisoformat(row[1]), row[2], row[3], row[4], row[5]
        )
        for row in rows
    ]


def replace_group_memberships(
    path: Path, group_id: str, users: tuple[EntraUser, ...]
) -> None:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute(
                "DELETE FROM entra_group_memberships WHERE group_id = ?", (group_id,)
            )
            connection.executemany(
                "INSERT INTO entra_group_memberships VALUES (?, ?)",
                ((group_id, user.object_id) for user in users),
            )


def list_cached_group_member_ids(path: Path, group_id: str) -> tuple[str, ...]:
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT user_id FROM entra_group_memberships WHERE group_id = ? ORDER BY user_id",
            (group_id,),
        ).fetchall()
    return tuple(row[0] for row in rows)


def update_cached_user(path: Path, user_id: str, department: str, job_title: str) -> None:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute(
                "UPDATE entra_users SET department = ?, job_title = ? WHERE object_id = ?",
                (department, job_title, user_id),
            )


def update_cached_membership(path: Path, group_id: str, user_id: str, add: bool) -> None:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            if add:
                connection.execute(
                    "INSERT OR IGNORE INTO entra_group_memberships VALUES (?, ?)",
                    (group_id, user_id),
                )
            else:
                connection.execute(
                    "DELETE FROM entra_group_memberships WHERE group_id = ? AND user_id = ?",
                    (group_id, user_id),
                )


def record_entra_operation(
    path: Path,
    mode: str,
    action: str,
    target: str,
    result: str,
    details: str,
    correlation_id: str | None = None,
) -> str:
    correlation_id = correlation_id or str(uuid4())
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute(
                "INSERT INTO entra_operations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(uuid4()),
                    datetime.now(timezone.utc).isoformat(),
                    mode,
                    action,
                    target,
                    result,
                    details[:500],
                    correlation_id,
                ),
            )
    return correlation_id


def list_entra_operations(path: Path, limit: int = 100) -> list[EntraOperation]:
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM entra_operations ORDER BY timestamp DESC, rowid DESC LIMIT ?",
            (max(1, min(limit, 500)),),
        ).fetchall()
    return [
        EntraOperation(
            row[0], datetime.fromisoformat(row[1]), row[2], row[3], row[4], row[5], row[6], row[7]
        )
        for row in rows
    ]
