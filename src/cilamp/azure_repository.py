"""SQLite projection and operation history for Azure resource authorization."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from cilamp.connectors.azure.models import (
    AzureIdentity,
    AzureOperation,
    AzureResource,
    AzureRoleAssignment,
    AzureSnapshot,
    AzureSyncState,
)


def initialize_azure_store(path: Path) -> None:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS azure_sync_state (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    status TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    subscription_label TEXT NOT NULL,
                    resource_group TEXT NOT NULL,
                    last_synced_at TEXT,
                    resource_count INTEGER NOT NULL DEFAULT 0,
                    identity_count INTEGER NOT NULL DEFAULT 0,
                    assignment_count INTEGER NOT NULL DEFAULT 0,
                    limitations TEXT NOT NULL DEFAULT '[]'
                );
                CREATE TABLE IF NOT EXISTS azure_resources (
                    resource_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_group TEXT NOT NULL,
                    location TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS azure_identities (
                    principal_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    identity_type TEXT NOT NULL,
                    source_resource TEXT NOT NULL,
                    credential_mode TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS azure_role_assignments (
                    assignment_id TEXT PRIMARY KEY,
                    principal_id TEXT NOT NULL,
                    principal_name TEXT NOT NULL,
                    principal_type TEXT NOT NULL,
                    role_definition_id TEXT NOT NULL,
                    role_name TEXT NOT NULL,
                    scope TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS azure_operations (
                    operation_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    action TEXT NOT NULL,
                    target TEXT NOT NULL,
                    result TEXT NOT NULL,
                    details TEXT NOT NULL,
                    correlation_id TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_azure_operations_time
                    ON azure_operations(timestamp DESC);
                CREATE INDEX IF NOT EXISTS idx_azure_assignments_principal
                    ON azure_role_assignments(principal_id, scope);
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO azure_sync_state(
                    singleton, status, mode, subscription_label, resource_group
                ) VALUES (1, 'NOT_SYNCED', 'SIMULATION', 'Simulation subscription', 'rg-cilamp-lab')
                """
            )


def save_azure_snapshot(
    path: Path,
    snapshot: AzureSnapshot,
    mode: str,
    subscription_label: str,
    resource_group: str,
) -> datetime:
    synced_at = datetime.now(timezone.utc)
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            for table in (
                "azure_resources",
                "azure_identities",
                "azure_role_assignments",
            ):
                connection.execute(f"DELETE FROM {table}")
            connection.executemany(
                "INSERT INTO azure_resources VALUES (?, ?, ?, ?, ?)",
                (
                    (
                        item.resource_id,
                        item.name,
                        item.resource_type,
                        item.resource_group,
                        item.location,
                    )
                    for item in snapshot.resources
                ),
            )
            connection.executemany(
                "INSERT INTO azure_identities VALUES (?, ?, ?, ?, ?)",
                (
                    (
                        item.principal_id,
                        item.display_name,
                        item.identity_type,
                        item.source_resource,
                        item.credential_mode,
                    )
                    for item in snapshot.identities
                ),
            )
            connection.executemany(
                "INSERT INTO azure_role_assignments VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    (
                        item.assignment_id,
                        item.principal_id,
                        item.principal_name,
                        item.principal_type,
                        item.role_definition_id,
                        item.role_name,
                        item.scope,
                    )
                    for item in snapshot.role_assignments
                ),
            )
            connection.execute(
                """
                UPDATE azure_sync_state SET
                    status = 'CONNECTED', mode = ?, subscription_label = ?,
                    resource_group = ?, last_synced_at = ?, resource_count = ?,
                    identity_count = ?, assignment_count = ?, limitations = ?
                WHERE singleton = 1
                """,
                (
                    mode,
                    subscription_label,
                    resource_group,
                    synced_at.isoformat(),
                    len(snapshot.resources),
                    len(snapshot.identities),
                    len(snapshot.role_assignments),
                    json.dumps(snapshot.limitations),
                ),
            )
    return synced_at


def mark_azure_failure(
    path: Path,
    mode: str,
    subscription_label: str,
    resource_group: str,
    limitation: str,
) -> None:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute(
                """
                UPDATE azure_sync_state
                SET status = 'ERROR', mode = ?, subscription_label = ?,
                    resource_group = ?, limitations = ? WHERE singleton = 1
                """,
                (mode, subscription_label, resource_group, json.dumps((limitation,))),
            )


def get_azure_sync_state(path: Path) -> AzureSyncState:
    with closing(sqlite3.connect(path)) as connection:
        row = connection.execute(
            """
            SELECT status, mode, subscription_label, resource_group, last_synced_at,
                   resource_count, identity_count, assignment_count, limitations
            FROM azure_sync_state WHERE singleton = 1
            """
        ).fetchone()
    return AzureSyncState(
        row[0], row[1], row[2], row[3],
        datetime.fromisoformat(row[4]) if row[4] else None,
        row[5], row[6], row[7], tuple(json.loads(row[8])),
    )


def list_azure_resources(path: Path) -> list[AzureResource]:
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM azure_resources ORDER BY resource_type, name"
        ).fetchall()
    return [AzureResource(*row) for row in rows]


def list_azure_identities(path: Path) -> list[AzureIdentity]:
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM azure_identities ORDER BY identity_type, display_name"
        ).fetchall()
    return [AzureIdentity(*row) for row in rows]


def list_azure_role_assignments(path: Path) -> list[AzureRoleAssignment]:
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM azure_role_assignments ORDER BY principal_name, role_name"
        ).fetchall()
    return [AzureRoleAssignment(*row) for row in rows]


def record_azure_operation(
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
                "INSERT INTO azure_operations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
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


def list_azure_operations(path: Path, limit: int = 100) -> list[AzureOperation]:
    with closing(sqlite3.connect(path)) as connection:
        rows = connection.execute(
            "SELECT * FROM azure_operations ORDER BY timestamp DESC, rowid DESC LIMIT ?",
            (max(1, min(limit, 500)),),
        ).fetchall()
    return [
        AzureOperation(
            row[0], datetime.fromisoformat(row[1]), row[2], row[3], row[4],
            row[5], row[6], row[7],
        )
        for row in rows
    ]
