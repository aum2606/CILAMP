"""Provider-independent least-privilege evaluation for Azure RBAC snapshots."""

from __future__ import annotations

from cilamp.connectors.azure.models import (
    AzureAccessDecision,
    AzureResource,
    AzureRoleAssignment,
)


ACTION_LABELS = {
    "resource.read": "Read resource configuration",
    "resource.write": "Modify resource configuration",
    "storage.blob.read": "Read blob data",
    "storage.blob.write": "Write blob data",
    "storage.blob.delete": "Delete blob data",
    "keyvault.secret.read": "Read Key Vault secret value",
    "keyvault.secret.write": "Create or update Key Vault secret",
    "rbac.manage": "Manage Azure role assignments",
}

ROLE_ACTIONS = {
    "Reader": frozenset({"resource.read"}),
    "Contributor": frozenset({"resource.read", "resource.write"}),
    "Owner": frozenset({"resource.read", "resource.write", "rbac.manage"}),
    "User Access Administrator": frozenset({"resource.read", "rbac.manage"}),
    "Storage Blob Data Reader": frozenset({"storage.blob.read"}),
    "Storage Blob Data Contributor": frozenset(
        {"storage.blob.read", "storage.blob.write", "storage.blob.delete"}
    ),
    "Key Vault Reader": frozenset({"resource.read"}),
    "Key Vault Secrets User": frozenset({"keyvault.secret.read"}),
    "Key Vault Secrets Officer": frozenset(
        {"keyvault.secret.read", "keyvault.secret.write"}
    ),
}


def scope_applies(scope: str, resource_id: str) -> bool:
    normalized_scope = scope.rstrip("/").casefold()
    normalized_resource = resource_id.rstrip("/").casefold()
    return normalized_resource == normalized_scope or normalized_resource.startswith(
        normalized_scope + "/"
    )


def evaluate_azure_access(
    principal_id: str,
    principal_name: str,
    resource: AzureResource,
    action: str,
    assignments: tuple[AzureRoleAssignment, ...] | list[AzureRoleAssignment],
) -> AzureAccessDecision:
    if action not in ACTION_LABELS:
        raise ValueError(f"Unsupported Azure action: {action}")
    applicable = tuple(
        assignment
        for assignment in assignments
        if assignment.principal_id == principal_id
        and scope_applies(assignment.scope, resource.resource_id)
    )
    granting = tuple(
        assignment
        for assignment in applicable
        if action in ROLE_ACTIONS.get(assignment.role_name, frozenset())
    )
    if granting:
        roles = tuple(sorted({assignment.role_name for assignment in granting}))
        return AzureAccessDecision(
            principal_id,
            principal_name,
            resource.resource_id,
            resource.name,
            action,
            "ALLOWED",
            roles,
            f"Granted by {', '.join(roles)} at an applicable Azure scope.",
        )
    unknown_roles = tuple(
        sorted(
            {
                assignment.role_name
                for assignment in applicable
                if assignment.role_name not in ROLE_ACTIONS
            }
        )
    )
    if unknown_roles:
        return AzureAccessDecision(
            principal_id,
            principal_name,
            resource.resource_id,
            resource.name,
            action,
            "UNKNOWN",
            unknown_roles,
            "A custom, unknown, or conditional role requires live Azure authorization evaluation.",
        )
    roles = tuple(sorted({assignment.role_name for assignment in applicable}))
    rationale = (
        f"Applicable roles ({', '.join(roles)}) do not grant this action."
        if roles
        else "No applicable role assignment grants this action at this scope."
    )
    return AzureAccessDecision(
        principal_id,
        principal_name,
        resource.resource_id,
        resource.name,
        action,
        "NOT GRANTED",
        roles,
        rationale,
    )
