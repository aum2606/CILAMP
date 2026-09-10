"""Deterministic Azure resource and RBAC laboratory."""

from __future__ import annotations

from cilamp.connectors.azure.models import (
    AzureIdentity,
    AzureResource,
    AzureRoleAssignment,
    AzureSnapshot,
)


SUBSCRIPTION_SCOPE = "/subscriptions/simulated-subscription"
RESOURCE_GROUP_SCOPE = f"{SUBSCRIPTION_SCOPE}/resourceGroups/rg-cilamp-lab"
DEV_STORAGE_SCOPE = (
    f"{RESOURCE_GROUP_SCOPE}/providers/Microsoft.Storage/storageAccounts/stcilampdev"
)
ARCHIVE_STORAGE_SCOPE = (
    f"{RESOURCE_GROUP_SCOPE}/providers/Microsoft.Storage/storageAccounts/stcilamparchive"
)
KEY_VAULT_SCOPE = (
    f"{RESOURCE_GROUP_SCOPE}/providers/Microsoft.KeyVault/vaults/kv-cilamp-lab"
)


class SimulationAzureConnector:
    mode = "SIMULATION"

    def check_connection(self) -> str:
        return "SIMULATED"

    def read_snapshot(self) -> AzureSnapshot:
        resources = (
            AzureResource(
                RESOURCE_GROUP_SCOPE,
                "rg-cilamp-lab",
                "Microsoft.Resources/resourceGroups",
                "rg-cilamp-lab",
                "Central India",
            ),
            AzureResource(
                DEV_STORAGE_SCOPE,
                "stcilampdev",
                "Microsoft.Storage/storageAccounts",
                "rg-cilamp-lab",
                "Central India",
            ),
            AzureResource(
                ARCHIVE_STORAGE_SCOPE,
                "stcilamparchive",
                "Microsoft.Storage/storageAccounts",
                "rg-cilamp-lab",
                "Central India",
            ),
            AzureResource(
                KEY_VAULT_SCOPE,
                "kv-cilamp-lab",
                "Microsoft.KeyVault/vaults",
                "rg-cilamp-lab",
                "Central India",
            ),
            AzureResource(
                f"{RESOURCE_GROUP_SCOPE}/providers/Microsoft.Web/sites/reporting-api",
                "reporting-api",
                "Microsoft.Web/sites",
                "rg-cilamp-lab",
                "Central India",
            ),
        )
        identities = (
            AzureIdentity(
                "sim-principal-developers",
                "Developers",
                "Group",
                "Microsoft Entra group",
                "HUMAN_GROUP_MEMBERSHIP",
            ),
            AzureIdentity(
                "sim-principal-security-admins",
                "Security Administrators",
                "Group",
                "Microsoft Entra group",
                "PRIVILEGED_HUMAN_GROUP",
            ),
            AzureIdentity(
                "sim-principal-reporting-mi",
                "reporting-api-mi",
                "SystemAssignedManagedIdentity",
                "reporting-api",
                "MANAGED_IDENTITY_NO_STORED_SECRET",
            ),
            AzureIdentity(
                "sim-principal-legacy-sp",
                "legacy-reporting-service-principal",
                "ServicePrincipal",
                "legacy-reporting-app",
                "STATIC_SECRET_METADATA_ONLY_NO_VALUE_STORED",
            ),
        )
        assignments = (
            _assignment(
                "ra-developer-storage-read",
                identities[0],
                "Storage Blob Data Reader",
                DEV_STORAGE_SCOPE,
            ),
            _assignment(
                "ra-security-reader",
                identities[1],
                "Reader",
                RESOURCE_GROUP_SCOPE,
            ),
            _assignment(
                "ra-managed-storage-read",
                identities[2],
                "Storage Blob Data Reader",
                DEV_STORAGE_SCOPE,
            ),
            _assignment(
                "ra-managed-vault-secret-read",
                identities[2],
                "Key Vault Secrets User",
                KEY_VAULT_SCOPE,
            ),
        )
        return AzureSnapshot(
            resources,
            identities,
            assignments,
            (
                "This simulation models role grants and inherited scopes; Azure deny assignments and role conditions require live evaluation.",
            ),
        )


def _assignment(
    assignment_id: str,
    identity: AzureIdentity,
    role_name: str,
    scope: str,
) -> AzureRoleAssignment:
    return AzureRoleAssignment(
        assignment_id,
        identity.principal_id,
        identity.display_name,
        identity.identity_type,
        f"sim-role-{role_name.lower().replace(' ', '-')}",
        role_name,
        scope,
    )
