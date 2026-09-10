"""Safe orchestration for simulation and live Microsoft Entra lab operations."""

from __future__ import annotations

from pathlib import Path

from cilamp.config import Settings
from cilamp.connectors.entra import (
    EntraConnector,
    EntraConnectorError,
    MicrosoftGraphConnector,
    SimulationEntraConnector,
)
from cilamp.entra_repository import (
    get_entra_sync_state,
    initialize_entra_store,
    list_entra_groups,
    list_entra_users,
    mark_entra_connection_failure,
    record_entra_operation,
    replace_group_memberships,
    save_entra_snapshot,
    update_cached_membership,
    update_cached_user,
)


READ_PERMISSIONS = (
    "User.Read.All",
    "GroupMember.Read.All",
    "Application.Read.All",
    "AuditLog.Read.All (optional audit tab)",
)
WRITE_PERMISSIONS = (
    "User.ReadWrite.All (selected lab-user profile updates)",
    "GroupMember.ReadWrite.All (allowlisted group membership only)",
)


class EntraSafetyError(RuntimeError):
    """Raised when a requested operation violates the lab safety boundary."""


def connector_for(settings: Settings) -> EntraConnector:
    if settings.mode == "SIMULATION":
        return SimulationEntraConnector(settings.database_path)
    if not settings.entra_lab_enabled or not settings.entra_tenant_id:
        raise EntraSafetyError(
            "The Entra connector is disabled for this LIVE_LAB configuration."
        )
    return MicrosoftGraphConnector(
        settings.entra_tenant_id, settings.entra_auth_method
    )


def synchronize_entra(
    settings: Settings, connector: EntraConnector | None = None
) -> str:
    initialize_entra_store(settings.database_path)
    connector = connector or connector_for(settings)
    try:
        connector.check_connection()
        snapshot = connector.read_snapshot()
        save_entra_snapshot(
            settings.database_path,
            snapshot,
            settings.mode,
            settings.entra_tenant_label,
        )
        return record_entra_operation(
            settings.database_path,
            settings.mode,
            "ENTRA_SYNCHRONIZATION",
            settings.entra_tenant_label,
            "SUCCESS",
            (
                f"Cached {len(snapshot.users)} users, {len(snapshot.groups)} groups, "
                f"and {len(snapshot.service_principals)} application identities."
            ),
        )
    except EntraConnectorError as error:
        message = str(error)
        mark_entra_connection_failure(
            settings.database_path,
            settings.mode,
            settings.entra_tenant_label,
            message,
        )
        record_entra_operation(
            settings.database_path,
            settings.mode,
            "ENTRA_SYNCHRONIZATION",
            settings.entra_tenant_label,
            "FAILURE",
            message,
        )
        raise


def refresh_group_members(
    settings: Settings, group_id: str, connector: EntraConnector | None = None
) -> str:
    initialize_entra_store(settings.database_path)
    groups = {
        group.object_id: group for group in list_entra_groups(settings.database_path)
    }
    if group_id not in groups:
        raise EntraSafetyError("Select a group from the synchronized directory cache.")
    connector = connector or connector_for(settings)
    try:
        users = connector.list_group_members(group_id)
        replace_group_memberships(settings.database_path, group_id, users)
        return record_entra_operation(
            settings.database_path,
            settings.mode,
            "ENTRA_GROUP_MEMBERS_READ",
            groups[group_id].display_name,
            "SUCCESS",
            f"Cached {len(users)} group members.",
        )
    except EntraConnectorError as error:
        record_entra_operation(
            settings.database_path,
            settings.mode,
            "ENTRA_GROUP_MEMBERS_READ",
            groups[group_id].display_name,
            "FAILURE",
            str(error),
        )
        raise


def update_entra_user(
    settings: Settings,
    user_id: str,
    department: str,
    job_title: str,
    *,
    confirmed: bool,
    connector: EntraConnector | None = None,
) -> str:
    initialize_entra_store(settings.database_path)
    user = _cached_user(settings.database_path, user_id)
    _validate_write(settings, confirmed, user.user_principal_name)
    department = department.strip()
    job_title = job_title.strip()
    if not department and not job_title:
        raise EntraSafetyError("Provide a department or job title update.")
    if len(department) > 64 or len(job_title) > 128:
        raise EntraSafetyError("The profile update exceeds the safe lab field limit.")
    connector = connector or connector_for(settings)
    try:
        connector.update_user(user_id, department=department, job_title=job_title)
        update_cached_user(settings.database_path, user_id, department, job_title)
        return record_entra_operation(
            settings.database_path,
            settings.mode,
            "ENTRA_USER_UPDATED",
            user.user_principal_name,
            "SUCCESS",
            "Updated department and job title; no credential fields were accepted.",
        )
    except EntraConnectorError as error:
        _record_write_failure(settings, "ENTRA_USER_UPDATED", user.user_principal_name, error)
        raise


def change_entra_group_membership(
    settings: Settings,
    group_id: str,
    user_id: str,
    operation: str,
    *,
    confirmed: bool,
    connector: EntraConnector | None = None,
) -> str:
    initialize_entra_store(settings.database_path)
    user = _cached_user(settings.database_path, user_id)
    groups = {group.object_id: group for group in list_entra_groups(settings.database_path)}
    if group_id not in groups:
        raise EntraSafetyError("Select a group from the synchronized directory cache.")
    _validate_write(settings, confirmed, user.user_principal_name, group_id)
    if operation not in {"ADD", "REMOVE"}:
        raise EntraSafetyError("Membership operation must be ADD or REMOVE.")
    connector = connector or connector_for(settings)
    action = f"ENTRA_GROUP_MEMBER_{operation}"
    try:
        if operation == "ADD":
            connector.add_group_member(group_id, user_id)
        else:
            connector.remove_group_member(group_id, user_id)
        update_cached_membership(
            settings.database_path, group_id, user_id, operation == "ADD"
        )
        return record_entra_operation(
            settings.database_path,
            settings.mode,
            action,
            user.user_principal_name,
            "SUCCESS",
            f"{operation.title()} membership in allowlisted group {groups[group_id].display_name}.",
        )
    except EntraConnectorError as error:
        _record_write_failure(settings, action, user.user_principal_name, error)
        raise


def _cached_user(path: Path, user_id: str):
    user = next((item for item in list_entra_users(path) if item.object_id == user_id), None)
    if user is None:
        raise EntraSafetyError("Select a user from the synchronized directory cache.")
    return user


def _validate_write(
    settings: Settings,
    confirmed: bool,
    user_principal_name: str,
    group_id: str | None = None,
) -> None:
    if not confirmed:
        raise EntraSafetyError("Explicit confirmation is required for this operation.")
    if settings.mode == "SIMULATION":
        return
    if not settings.entra_writes_enabled:
        raise EntraSafetyError("LIVE_LAB writes are disabled by configuration.")
    suffix = f"@{settings.entra_allowed_user_domain}" if settings.entra_allowed_user_domain else ""
    if not suffix or not user_principal_name.lower().endswith(suffix):
        raise EntraSafetyError("The selected user is outside the allowed lab UPN domain.")
    if group_id is not None and group_id not in settings.entra_allowed_group_ids:
        raise EntraSafetyError("The selected group is not in the live-write allowlist.")


def _record_write_failure(
    settings: Settings, action: str, target: str, error: EntraConnectorError
) -> None:
    record_entra_operation(
        settings.database_path,
        settings.mode,
        action,
        target,
        "FAILURE",
        str(error),
    )
