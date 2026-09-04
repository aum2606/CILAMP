from dataclasses import replace
from pathlib import Path

import pytest

from cilamp.config import Settings
from cilamp.entra_repository import (
    get_entra_sync_state,
    initialize_entra_store,
    list_cached_group_member_ids,
    list_entra_groups,
    list_entra_operations,
    list_entra_service_principals,
    list_entra_users,
)
from cilamp.entra_service import (
    EntraSafetyError,
    change_entra_group_membership,
    refresh_group_members,
    synchronize_entra,
    update_entra_user,
)
from cilamp.repository import initialize_organization


TEST_DATA_DIR = Path(__file__).parents[1] / "data"


class RecordingConnector:
    mode = "LIVE_LAB"

    def __init__(self):
        self.calls = []

    def update_user(self, user_id, *, department, job_title):
        self.calls.append(("UPDATE", user_id, department, job_title))

    def add_group_member(self, group_id, user_id):
        self.calls.append(("ADD", group_id, user_id))

    def remove_group_member(self, group_id, user_id):
        self.calls.append(("REMOVE", group_id, user_id))


@pytest.fixture
def simulation_settings():
    path = TEST_DATA_DIR / "test-entra.db"
    path.unlink(missing_ok=True)
    initialize_organization(path)
    initialize_entra_store(path)
    yield Settings(mode="SIMULATION", database_path=path)
    path.unlink(missing_ok=True)


def test_simulation_sync_caches_users_groups_apps_and_operations(simulation_settings) -> None:
    correlation_id = synchronize_entra(simulation_settings)
    state = get_entra_sync_state(simulation_settings.database_path)

    assert correlation_id
    assert state.status == "CONNECTED"
    assert state.user_count == 500
    assert state.group_count == 13
    assert state.service_principal_count == 10
    assert len(list_entra_users(simulation_settings.database_path)) == 500
    assert len(list_entra_groups(simulation_settings.database_path)) == 13
    assert len(list_entra_service_principals(simulation_settings.database_path)) == 10
    assert list_entra_operations(simulation_settings.database_path)[0].result == "SUCCESS"


def test_membership_read_and_confirmed_simulation_writes(simulation_settings) -> None:
    synchronize_entra(simulation_settings)
    path = simulation_settings.database_path
    user = list_entra_users(path)[0]
    group = list_entra_groups(path)[0]

    refresh_group_members(simulation_settings, group.object_id)
    assert len(list_cached_group_member_ids(path, group.object_id)) == 500

    with pytest.raises(EntraSafetyError, match="confirmation"):
        update_entra_user(
            simulation_settings,
            user.object_id,
            "IT",
            "Administrator",
            confirmed=False,
        )

    update_entra_user(
        simulation_settings,
        user.object_id,
        "IT",
        "Administrator",
        confirmed=True,
    )
    change_entra_group_membership(
        simulation_settings,
        group.object_id,
        user.object_id,
        "ADD",
        confirmed=True,
    )
    updated = next(item for item in list_entra_users(path) if item.object_id == user.object_id)
    assert (updated.department, updated.job_title) == ("IT", "Administrator")
    assert user.object_id in list_cached_group_member_ids(path, group.object_id)


def test_live_writes_require_switch_domain_and_group_allowlist(simulation_settings) -> None:
    synchronize_entra(simulation_settings)
    path = simulation_settings.database_path
    user = list_entra_users(path)[0]
    group = list_entra_groups(path)[0]
    connector = RecordingConnector()
    live = replace(
        simulation_settings,
        mode="LIVE_LAB",
        entra_lab_enabled=True,
        entra_tenant_id="lab-tenant",
        entra_writes_enabled=False,
        entra_allowed_user_domain="example.cilamp",
        entra_allowed_group_ids=(group.object_id,),
    )

    with pytest.raises(EntraSafetyError, match="disabled"):
        update_entra_user(
            live, user.object_id, "IT", "Administrator", confirmed=True, connector=connector
        )

    enabled = replace(live, entra_writes_enabled=True)
    update_entra_user(
        enabled, user.object_id, "IT", "Administrator", confirmed=True, connector=connector
    )
    change_entra_group_membership(
        enabled,
        group.object_id,
        user.object_id,
        "REMOVE",
        confirmed=True,
        connector=connector,
    )
    assert connector.calls[0][0] == "UPDATE"
    assert connector.calls[1][0] == "REMOVE"

    blocked_group = replace(enabled, entra_allowed_group_ids=())
    with pytest.raises(EntraSafetyError, match="allowlist"):
        change_entra_group_membership(
            blocked_group,
            group.object_id,
            user.object_id,
            "ADD",
            confirmed=True,
            connector=connector,
        )
