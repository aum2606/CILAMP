"""SQLite display cache and operation history for AWS IAM."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from cilamp.connectors.aws.models import AwsCloudTrailEvent, AwsOperation, AwsPolicy, AwsPolicyStatement, AwsResource, AwsRole, AwsRolePolicyBinding, AwsSnapshot, AwsSyncState


def initialize_aws_store(path: Path) -> None:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS aws_sync_state (singleton INTEGER PRIMARY KEY CHECK(singleton=1), status TEXT NOT NULL, mode TEXT NOT NULL, account_label TEXT NOT NULL, region TEXT NOT NULL, last_synced_at TEXT, resource_count INTEGER NOT NULL DEFAULT 0, role_count INTEGER NOT NULL DEFAULT 0, policy_count INTEGER NOT NULL DEFAULT 0, event_count INTEGER NOT NULL DEFAULT 0, caller_arn TEXT NOT NULL DEFAULT '', limitations TEXT NOT NULL DEFAULT '[]');
                CREATE TABLE IF NOT EXISTS aws_resources (arn TEXT PRIMARY KEY, name TEXT NOT NULL, resource_type TEXT NOT NULL, region TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS aws_roles (arn TEXT PRIMARY KEY, name TEXT NOT NULL, path TEXT NOT NULL, trusted_principals TEXT NOT NULL, credential_mode TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS aws_policies (arn TEXT PRIMARY KEY, name TEXT NOT NULL, source TEXT NOT NULL, statements TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS aws_role_policy_bindings (role_arn TEXT NOT NULL, policy_arn TEXT NOT NULL, PRIMARY KEY(role_arn, policy_arn));
                CREATE TABLE IF NOT EXISTS aws_cloudtrail_events (event_id TEXT PRIMARY KEY, event_time TEXT NOT NULL, event_name TEXT NOT NULL, username TEXT NOT NULL, resource_name TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS aws_operations (operation_id TEXT PRIMARY KEY, timestamp TEXT NOT NULL, mode TEXT NOT NULL, action TEXT NOT NULL, target TEXT NOT NULL, result TEXT NOT NULL, details TEXT NOT NULL, correlation_id TEXT NOT NULL);
                CREATE INDEX IF NOT EXISTS idx_aws_operations_time ON aws_operations(timestamp DESC);
            """)
            connection.execute("INSERT OR IGNORE INTO aws_sync_state(singleton,status,mode,account_label,region) VALUES(1,'NOT_SYNCED','SIMULATION','Simulation AWS account','ap-south-1')")


def save_aws_snapshot(path: Path, snapshot: AwsSnapshot, mode: str, account_label: str, region: str) -> datetime:
    synced_at = datetime.now(timezone.utc)
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            for table in ("aws_resources", "aws_roles", "aws_policies", "aws_role_policy_bindings", "aws_cloudtrail_events"):
                connection.execute(f"DELETE FROM {table}")
            connection.executemany("INSERT INTO aws_resources VALUES(?,?,?,?)", ((x.arn,x.name,x.resource_type,x.region) for x in snapshot.resources))
            connection.executemany("INSERT INTO aws_roles VALUES(?,?,?,?,?)", ((x.arn,x.name,x.path,json.dumps(x.trusted_principals),x.credential_mode) for x in snapshot.roles))
            connection.executemany("INSERT INTO aws_policies VALUES(?,?,?,?)", ((x.arn,x.name,x.source,json.dumps([{"sid":s.sid,"effect":s.effect,"actions":s.actions,"resources":s.resources,"has_conditions":s.has_conditions} for s in x.statements])) for x in snapshot.policies))
            connection.executemany("INSERT INTO aws_role_policy_bindings VALUES(?,?)", ((x.role_arn,x.policy_arn) for x in snapshot.bindings))
            connection.executemany("INSERT INTO aws_cloudtrail_events VALUES(?,?,?,?,?)", ((x.event_id,x.event_time.isoformat(),x.event_name,x.username,x.resource_name) for x in snapshot.cloudtrail_events))
            connection.execute("UPDATE aws_sync_state SET status='CONNECTED',mode=?,account_label=?,region=?,last_synced_at=?,resource_count=?,role_count=?,policy_count=?,event_count=?,caller_arn=?,limitations=? WHERE singleton=1", (mode,account_label,region,synced_at.isoformat(),len(snapshot.resources),len(snapshot.roles),len(snapshot.policies),len(snapshot.cloudtrail_events),snapshot.caller_arn,json.dumps(snapshot.limitations)))
    return synced_at


def mark_aws_failure(path: Path, mode: str, account_label: str, region: str, limitation: str) -> None:
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("UPDATE aws_sync_state SET status='ERROR',mode=?,account_label=?,region=?,limitations=? WHERE singleton=1", (mode,account_label,region,json.dumps((limitation,))))


def get_aws_sync_state(path: Path) -> AwsSyncState:
    with closing(sqlite3.connect(path)) as connection:
        row = connection.execute("SELECT status,mode,account_label,region,last_synced_at,resource_count,role_count,policy_count,event_count,caller_arn,limitations FROM aws_sync_state WHERE singleton=1").fetchone()
    return AwsSyncState(row[0],row[1],row[2],row[3],datetime.fromisoformat(row[4]) if row[4] else None,row[5],row[6],row[7],row[8],row[9],tuple(json.loads(row[10])))


def list_aws_resources(path: Path) -> list[AwsResource]:
    return [AwsResource(*row) for row in _rows(path,"SELECT * FROM aws_resources ORDER BY resource_type,name")]


def list_aws_roles(path: Path) -> list[AwsRole]:
    return [AwsRole(row[0],row[1],row[2],tuple(json.loads(row[3])),row[4]) for row in _rows(path,"SELECT * FROM aws_roles ORDER BY name")]


def list_aws_policies(path: Path) -> list[AwsPolicy]:
    result=[]
    for row in _rows(path,"SELECT * FROM aws_policies ORDER BY name"):
        statements=tuple(AwsPolicyStatement(s["sid"],s["effect"],tuple(s["actions"]),tuple(s["resources"]),s["has_conditions"]) for s in json.loads(row[3]))
        result.append(AwsPolicy(row[0],row[1],row[2],statements))
    return result


def list_aws_bindings(path: Path) -> list[AwsRolePolicyBinding]:
    return [AwsRolePolicyBinding(*row) for row in _rows(path,"SELECT * FROM aws_role_policy_bindings ORDER BY role_arn,policy_arn")]


def list_aws_cloudtrail_events(path: Path) -> list[AwsCloudTrailEvent]:
    return [AwsCloudTrailEvent(row[0],datetime.fromisoformat(row[1]),row[2],row[3],row[4]) for row in _rows(path,"SELECT * FROM aws_cloudtrail_events ORDER BY event_time DESC")]


def _rows(path: Path, query: str):
    with closing(sqlite3.connect(path)) as connection:
        return connection.execute(query).fetchall()


def record_aws_operation(path: Path, mode: str, action: str, target: str, result: str, details: str, correlation_id: str | None=None) -> str:
    correlation_id=correlation_id or str(uuid4())
    with closing(sqlite3.connect(path)) as connection:
        with connection:
            connection.execute("INSERT INTO aws_operations VALUES(?,?,?,?,?,?,?,?)",(str(uuid4()),datetime.now(timezone.utc).isoformat(),mode,action,target,result,details[:500],correlation_id))
    return correlation_id


def list_aws_operations(path: Path, limit: int=100) -> list[AwsOperation]:
    with closing(sqlite3.connect(path)) as connection:
        rows=connection.execute("SELECT * FROM aws_operations ORDER BY timestamp DESC,rowid DESC LIMIT ?",(max(1,min(limit,500)),)).fetchall()
    return [AwsOperation(row[0],datetime.fromisoformat(row[1]),row[2],row[3],row[4],row[5],row[6],row[7]) for row in rows]
