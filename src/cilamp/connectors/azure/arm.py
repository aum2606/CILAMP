"""Read-only Azure Resource Manager adapter for a dedicated lab scope."""

from __future__ import annotations

import json
from base64 import urlsafe_b64decode
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from cilamp.connectors.azure.base import AzureConnectorError
from cilamp.connectors.azure.models import (
    AzureIdentity,
    AzureResource,
    AzureRoleAssignment,
    AzureSnapshot,
)


ARM_ROOT = "https://management.azure.com"
ARM_SCOPE = "https://management.azure.com/.default"


def build_azure_credential(auth_method: str, tenant_id: str):
    try:
        from azure.identity import AzureCliCredential, DefaultAzureCredential
    except ImportError as error:  # pragma: no cover - environment-specific
        raise AzureConnectorError(
            "azure-identity is required for LIVE_LAB Azure authentication."
        ) from error
    if auth_method == "AZURE_CLI":
        return AzureCliCredential(tenant_id=tenant_id)
    return DefaultAzureCredential(exclude_interactive_browser_credential=True)


class AzureResourceManagerConnector:
    """Discover resources, managed identities, and RBAC without changing Azure."""

    mode = "LIVE_LAB"

    def __init__(
        self,
        tenant_id: str,
        subscription_id: str,
        resource_group: str,
        auth_method: str = "AZURE_CLI",
        *,
        credential=None,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        if not all(
            (tenant_id.strip(), subscription_id.strip(), resource_group.strip())
        ):
            raise ValueError("Tenant, subscription, and resource group are required.")
        self.tenant_id = tenant_id
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.credential = credential or build_azure_credential(auth_method, tenant_id)
        self.opener = opener

    @property
    def resource_group_scope(self) -> str:
        return (
            f"/subscriptions/{self.subscription_id}/resourceGroups/{self.resource_group}"
        )

    def _token(self) -> str:
        try:
            token = self.credential.get_token(
                ARM_SCOPE, tenant_id=self.tenant_id
            ).token
        except Exception as error:
            raise AzureConnectorError(
                f"Azure authentication failed ({type(error).__name__}). Check the lab tenant login."
            ) from error
        try:
            payload = token.split(".")[1]
            padding = "=" * (-len(payload) % 4)
            token_tenant = json.loads(
                urlsafe_b64decode(payload + padding).decode("utf-8")
            ).get("tid", "")
        except (IndexError, ValueError, UnicodeDecodeError) as error:
            raise AzureConnectorError(
                "Authentication succeeded, but the Azure token tenant could not be verified."
            ) from error
        if token_tenant.casefold() != self.tenant_id.casefold():
            raise AzureConnectorError(
                "Authenticated Azure token belongs to a different tenant than the configured lab."
            )
        return token

    def _request(self, path: str) -> dict[str, Any]:
        request = Request(
            f"{ARM_ROOT}{path}",
            method="GET",
            headers={
                "Authorization": f"Bearer {self._token()}",
                "Accept": "application/json",
            },
        )
        try:
            with self.opener(request, timeout=20) as response:
                content = response.read()
                try:
                    return json.loads(content) if content else {}
                except (ValueError, UnicodeDecodeError) as error:
                    raise AzureConnectorError(
                        "Azure Resource Manager returned an invalid JSON response."
                    ) from error
        except HTTPError as error:
            code = f"HTTP {error.code}"
            try:
                parsed = json.loads(error.read().decode("utf-8"))
                provider_code = parsed.get("error", {}).get("code", "")
                if provider_code:
                    code = f"{code} {provider_code}"
            except (ValueError, UnicodeDecodeError):
                pass
            raise AzureConnectorError(
                f"Azure Resource Manager request failed ({code}). Verify Reader access and "
                "the configured lab scope.",
                status_code=error.code,
            ) from error
        except (URLError, TimeoutError, OSError) as error:
            raise AzureConnectorError(
                f"Azure Resource Manager is unreachable ({type(error).__name__})."
            ) from error

    def _collection(self, path: str, max_pages: int = 10) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        next_path = path
        for _ in range(max_pages):
            response = self._request(next_path)
            items.extend(response.get("value", []))
            next_link = response.get("nextLink")
            if not next_link:
                break
            if not next_link.startswith(ARM_ROOT):
                raise AzureConnectorError("ARM returned an unexpected pagination URL.")
            next_path = next_link[len(ARM_ROOT) :]
        return items

    def check_connection(self) -> str:
        subscription = quote(self.subscription_id, safe="")
        resource_group = quote(self.resource_group, safe="")
        self._request(
            f"/subscriptions/{subscription}/resourceGroups/{resource_group}"
            "?api-version=2021-04-01"
        )
        return "CONNECTED"

    def read_snapshot(self) -> AzureSnapshot:
        subscription = quote(self.subscription_id, safe="")
        resource_group = quote(self.resource_group, safe="")
        scope = f"/subscriptions/{subscription}/resourceGroups/{resource_group}"
        raw_resources = self._collection(
            f"{scope}/resources?api-version=2021-04-01"
        )
        resources = [
            AzureResource(
                self.resource_group_scope,
                self.resource_group,
                "Microsoft.Resources/resourceGroups",
                self.resource_group,
                "",
            )
        ]
        resources.extend(
            AzureResource(
                item.get("id", ""),
                item.get("name", "Unnamed resource"),
                item.get("type", "Unknown"),
                self.resource_group,
                item.get("location", ""),
            )
            for item in raw_resources
        )

        limitations = [
            "Effective access is inferred from role assignments; Azure deny assignments, conditions, group expansion, and resource-specific authorization still require provider evaluation."
        ]
        identities: list[AzureIdentity] = []
        for item in raw_resources:
            identity = item.get("identity") or {}
            principal_id = identity.get("principalId")
            if principal_id:
                identity_type = identity.get("type") or "SystemAssigned"
                identities.append(
                    AzureIdentity(
                        principal_id,
                        f"{item.get('name', 'resource')}-identity",
                        "SystemAssignedManagedIdentity"
                        if "SystemAssigned" in identity_type
                        else f"{identity_type}ManagedIdentity",
                        item.get("name", "Azure resource"),
                        "MANAGED_IDENTITY_NO_STORED_SECRET",
                    )
                )
        try:
            raw_identities = self._collection(
                f"{scope}/providers/Microsoft.ManagedIdentity/userAssignedIdentities?api-version=2023-01-31"
            )
            for item in raw_identities:
                properties = item.get("properties") or {}
                if properties.get("principalId"):
                    identities.append(
                        AzureIdentity(
                            properties["principalId"],
                            item.get("name", "User-assigned managed identity"),
                            "UserAssignedManagedIdentity",
                            item.get("id", ""),
                            "MANAGED_IDENTITY_NO_STORED_SECRET",
                        )
                    )
        except AzureConnectorError as error:
            limitations.append(f"Managed identity inventory unavailable: {error}")

        role_definitions = self._collection(
            f"{scope}/providers/Microsoft.Authorization/roleDefinitions?api-version=2022-04-01"
        )
        role_names = {
            item.get("id", "").casefold(): (item.get("properties") or {}).get(
                "roleName", "Unknown role"
            )
            for item in role_definitions
        }
        raw_assignments = self._collection(
            f"{scope}/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01"
        )
        identity_names = {identity.principal_id: identity.display_name for identity in identities}
        assignments = []
        for item in raw_assignments:
            properties = item.get("properties") or {}
            principal_id = properties.get("principalId", "")
            role_id = properties.get("roleDefinitionId", "")
            role_name = role_names.get(role_id.casefold(), "Unknown/custom role")
            if properties.get("condition"):
                role_name = f"{role_name} (CONDITIONAL)"
            if principal_id and principal_id not in identity_names:
                principal_name = _masked_principal(principal_id)
                identities.append(
                    AzureIdentity(
                        principal_id,
                        principal_name,
                        properties.get("principalType", "Unknown"),
                        "Microsoft Entra principal referenced by Azure RBAC",
                        "EXTERNAL_PRINCIPAL_METADATA_ONLY",
                    )
                )
                identity_names[principal_id] = principal_name
            assignments.append(
                AzureRoleAssignment(
                    item.get("id", ""),
                    principal_id,
                    identity_names.get(principal_id, _masked_principal(principal_id)),
                    properties.get("principalType", "Unknown"),
                    role_id,
                    role_name,
                    properties.get("scope", self.resource_group_scope),
                )
            )
            if properties.get("condition"):
                limitations.append(
                    "One or more conditional role assignments require live Azure condition evaluation."
                )
        return AzureSnapshot(
            tuple(resources),
            tuple(_unique_identities(identities)),
            tuple(assignments),
            tuple(dict.fromkeys(limitations)),
        )


def _masked_principal(principal_id: str) -> str:
    if len(principal_id) > 12:
        return f"Principal {principal_id[:6]}…{principal_id[-4:]}"
    return "Unresolved principal"


def _unique_identities(identities: list[AzureIdentity]) -> list[AzureIdentity]:
    return list({identity.principal_id: identity for identity in identities}.values())
