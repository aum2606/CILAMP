from pathlib import Path

import pytest

pytestmark = pytest.mark.skip(reason="Azure integration removed from active scope — Settings no longer carries Azure fields")

from cilamp.azure_policy import evaluate_azure_access
from cilamp.azure_repository import (
    get_azure_sync_state,
    initialize_azure_store,
    list_azure_identities,
    list_azure_operations,
    list_azure_resources,
    list_azure_role_assignments,
)
from cilamp.azure_service import AzureSafetyError, azure_connector_for, synchronize_azure
from cilamp.config import Settings
from cilamp.repository import initialize_organization


TEST_DATA_DIR = Path(__file__).parents[1] / "data"


@pytest.fixture
def settings():
    path = TEST_DATA_DIR / "test-azure.db"
    path.unlink(missing_ok=True)
    initialize_organization(path)
    initialize_azure_store(path)
    yield Settings(mode="SIMULATION", database_path=path)
    path.unlink(missing_ok=True)


def test_simulation_sync_persists_resources_identities_rbac_and_operation(settings) -> None:
    correlation_id = synchronize_azure(settings)
    state = get_azure_sync_state(settings.database_path)

    assert correlation_id
    assert state.status == "CONNECTED"
    assert (state.resource_count, state.identity_count, state.assignment_count) == (5, 4, 4)
    assert len(list_azure_resources(settings.database_path)) == 5
    assert len(list_azure_identities(settings.database_path)) == 4
    assert len(list_azure_role_assignments(settings.database_path)) == 4
    assert list_azure_operations(settings.database_path)[0].result == "SUCCESS"


def test_cached_snapshot_supports_effective_access_decision(settings) -> None:
    synchronize_azure(settings)
    identities = list_azure_identities(settings.database_path)
    resources = list_azure_resources(settings.database_path)
    assignments = list_azure_role_assignments(settings.database_path)
    developer = next(item for item in identities if item.display_name == "Developers")
    storage = next(item for item in resources if item.name == "stcilampdev")

    decision = evaluate_azure_access(
        developer.principal_id,
        developer.display_name,
        storage,
        "storage.blob.read",
        assignments,
    )

    assert decision.decision == "ALLOWED"
    assert decision.matched_roles == ("Storage Blob Data Reader",)


def test_live_connector_requires_azure_specific_guard(settings) -> None:
    live = Settings(
        mode="LIVE_LAB",
        database_path=settings.database_path,
        entra_lab_enabled=True,
        entra_tenant_id="entra-lab",
        azure_lab_enabled=False,
    )

    with pytest.raises(AzureSafetyError, match="disabled"):
        azure_connector_for(live)
