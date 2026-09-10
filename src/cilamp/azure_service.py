"""Safe orchestration for Azure resource and RBAC discovery."""

from __future__ import annotations

from cilamp.azure_repository import (
    initialize_azure_store,
    mark_azure_failure,
    record_azure_operation,
    save_azure_snapshot,
)
from cilamp.config import Settings
from cilamp.connectors.azure import (
    AzureConnector,
    AzureConnectorError,
    AzureResourceManagerConnector,
    SimulationAzureConnector,
)


class AzureSafetyError(RuntimeError):
    """Raised when Azure live-lab configuration is incomplete or unsafe."""


def azure_connector_for(settings: Settings) -> AzureConnector:
    if settings.mode == "SIMULATION":
        return SimulationAzureConnector()
    if not settings.azure_lab_enabled:
        raise AzureSafetyError(
            "Azure LIVE_LAB access is disabled; enable only a dedicated Azure lab."
        )
    return AzureResourceManagerConnector(
        settings.azure_tenant_id,
        settings.azure_subscription_id,
        settings.azure_resource_group,
        settings.azure_auth_method,
    )


def synchronize_azure(
    settings: Settings, connector: AzureConnector | None = None
) -> str:
    initialize_azure_store(settings.database_path)
    connector = connector or azure_connector_for(settings)
    try:
        connector.check_connection()
        snapshot = connector.read_snapshot()
        save_azure_snapshot(
            settings.database_path,
            snapshot,
            settings.mode,
            settings.azure_subscription_label,
            settings.azure_resource_group,
        )
        return record_azure_operation(
            settings.database_path,
            settings.mode,
            "AZURE_RBAC_SYNCHRONIZATION",
            settings.azure_resource_group,
            "SUCCESS",
            (
                f"Cached {len(snapshot.resources)} resources, {len(snapshot.identities)} "
                f"identities, and {len(snapshot.role_assignments)} role assignments."
            ),
        )
    except AzureConnectorError as error:
        mark_azure_failure(
            settings.database_path,
            settings.mode,
            settings.azure_subscription_label,
            settings.azure_resource_group,
            str(error),
        )
        record_azure_operation(
            settings.database_path,
            settings.mode,
            "AZURE_RBAC_SYNCHRONIZATION",
            settings.azure_resource_group,
            "FAILURE",
            str(error),
        )
        raise
