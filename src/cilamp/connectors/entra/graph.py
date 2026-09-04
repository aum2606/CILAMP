"""Narrow Microsoft Graph v1.0 connector for a dedicated Entra lab."""

from __future__ import annotations

import json
from base64 import urlsafe_b64decode
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from cilamp.connectors.entra.base import EntraConnectorError
from cilamp.connectors.entra.models import (
    EntraDirectoryAudit,
    EntraGroup,
    EntraServicePrincipal,
    EntraSnapshot,
    EntraUser,
)


GRAPH_ROOT = "https://graph.microsoft.com/v1.0"
GRAPH_SCOPE = "https://graph.microsoft.com/.default"


def build_credential(auth_method: str, tenant_id: str):
    """Create an identity credential lazily so simulation has no Azure dependency."""

    try:
        from azure.identity import AzureCliCredential, DefaultAzureCredential
    except ImportError as error:  # pragma: no cover - environment-specific
        raise EntraConnectorError(
            "azure-identity is required for LIVE_LAB authentication."
        ) from error
    if auth_method == "AZURE_CLI":
        return AzureCliCredential(tenant_id=tenant_id)
    return DefaultAzureCredential(exclude_interactive_browser_credential=True)


class MicrosoftGraphConnector:
    """Translate provider-neutral Entra operations into explicit Graph requests."""

    mode = "LIVE_LAB"

    def __init__(
        self,
        tenant_id: str,
        auth_method: str = "AZURE_CLI",
        *,
        credential=None,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        if not tenant_id:
            raise ValueError("A dedicated lab tenant ID is required.")
        self.tenant_id = tenant_id
        self.credential = credential or build_credential(auth_method, tenant_id)
        self.opener = opener

    def _token(self) -> str:
        try:
            token = self.credential.get_token(
                GRAPH_SCOPE, tenant_id=self.tenant_id
            ).token
        except Exception as error:
            raise EntraConnectorError(
                f"Authentication failed ({type(error).__name__}). Check the lab tenant login."
            ) from error
        try:
            payload = token.split(".")[1]
            padding = "=" * (-len(payload) % 4)
            token_tenant = json.loads(
                urlsafe_b64decode(payload + padding).decode("utf-8")
            ).get("tid", "")
        except (IndexError, ValueError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise EntraConnectorError(
                "Authentication succeeded, but the token tenant could not be verified."
            ) from error
        if token_tenant.casefold() != self.tenant_id.casefold():
            raise EntraConnectorError(
                "Authenticated token belongs to a different tenant than the configured lab."
            )
        return token

    def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            f"{GRAPH_ROOT}{path}",
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {self._token()}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )
        try:
            with self.opener(request, timeout=20) as response:
                content = response.read()
                return json.loads(content) if content else {}
        except HTTPError as error:
            code = f"HTTP {error.code}"
            try:
                parsed = json.loads(error.read().decode("utf-8"))
                graph_code = parsed.get("error", {}).get("code", "")
                if graph_code:
                    code = f"{code} {graph_code}"
            except (ValueError, UnicodeDecodeError):
                pass
            raise EntraConnectorError(
                f"Microsoft Graph request failed ({code}). Verify permissions and lab scope.",
                status_code=error.code,
            ) from error
        except (URLError, TimeoutError, OSError) as error:
            raise EntraConnectorError(
                f"Microsoft Graph is unreachable ({type(error).__name__})."
            ) from error

    def _collection(self, path: str, max_pages: int = 10) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        next_path = path
        for _ in range(max_pages):
            response = self._request("GET", next_path)
            items.extend(response.get("value", []))
            next_link = response.get("@odata.nextLink")
            if not next_link:
                break
            if not next_link.startswith(GRAPH_ROOT):
                raise EntraConnectorError("Graph returned an unexpected pagination URL.")
            next_path = next_link[len(GRAPH_ROOT) :]
        return items

    def check_connection(self) -> str:
        self._request("GET", "/users?$select=id&$top=1")
        return "CONNECTED"

    def read_snapshot(self) -> EntraSnapshot:
        users = tuple(
            _user(item)
            for item in self._collection(
                "/users?$select=id,displayName,userPrincipalName,accountEnabled,department,jobTitle&$top=999"
            )
        )
        groups = tuple(
            EntraGroup(
                item.get("id", ""),
                item.get("displayName", "Unnamed group"),
                item.get("description") or "",
                bool(item.get("securityEnabled")),
                "Microsoft 365"
                if "Unified" in (item.get("groupTypes") or [])
                else "Security",
            )
            for item in self._collection(
                "/groups?$select=id,displayName,description,securityEnabled,groupTypes&$top=999"
            )
        )
        principals = tuple(
            EntraServicePrincipal(
                item.get("id", ""),
                item.get("displayName", "Unnamed application identity"),
                item.get("appId", ""),
                item.get("servicePrincipalType", "ServicePrincipal"),
                bool(item.get("accountEnabled", True)),
            )
            for item in self._collection(
                "/servicePrincipals?$select=id,displayName,appId,servicePrincipalType,accountEnabled&$top=999"
            )
        )
        limitations: list[str] = []
        try:
            audits = tuple(
                _audit(item)
                for item in self._collection(
                    "/auditLogs/directoryAudits?$top=25&$orderby=activityDateTime%20desc",
                    max_pages=1,
                )
            )
        except EntraConnectorError as error:
            audits = ()
            limitations.append(
                f"Directory audit retrieval unavailable: {error}. AuditLog.Read.All and a supported Entra role may be required."
            )
        return EntraSnapshot(users, groups, principals, audits, tuple(limitations))

    def list_group_members(self, group_id: str) -> tuple[EntraUser, ...]:
        safe_id = quote(group_id, safe="")
        return tuple(
            _user(item)
            for item in self._collection(
                f"/groups/{safe_id}/members/microsoft.graph.user?$select=id,displayName,userPrincipalName,accountEnabled,department,jobTitle&$top=999"
            )
        )

    def update_user(self, user_id: str, *, department: str, job_title: str) -> None:
        self._request(
            "PATCH",
            f"/users/{quote(user_id, safe='')}",
            {"department": department, "jobTitle": job_title},
        )

    def add_group_member(self, group_id: str, user_id: str) -> None:
        self._request(
            "POST",
            f"/groups/{quote(group_id, safe='')}/members/$ref",
            {"@odata.id": f"{GRAPH_ROOT}/directoryObjects/{user_id}"},
        )

    def remove_group_member(self, group_id: str, user_id: str) -> None:
        self._request(
            "DELETE",
            f"/groups/{quote(group_id, safe='')}/members/{quote(user_id, safe='')}/$ref",
        )


def _user(item: dict[str, Any]) -> EntraUser:
    return EntraUser(
        item.get("id", ""),
        item.get("displayName", "Unnamed user"),
        item.get("userPrincipalName", ""),
        bool(item.get("accountEnabled", True)),
        item.get("department") or "",
        item.get("jobTitle") or "",
    )


def _audit(item: dict[str, Any]) -> EntraDirectoryAudit:
    initiated = item.get("initiatedBy", {})
    user_actor = initiated.get("user") or {}
    app_actor = initiated.get("app") or {}
    actor = user_actor.get("userPrincipalName") or app_actor.get(
        "displayName", "Unknown"
    )
    targets = item.get("targetResources", [])
    target = targets[0].get("displayName", "Unknown") if targets else "Unknown"
    raw_time = item.get("activityDateTime")
    try:
        activity_at = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        activity_at = datetime.now(timezone.utc)
    return EntraDirectoryAudit(
        item.get("id", ""),
        activity_at,
        item.get("activityDisplayName", "Directory activity"),
        item.get("result", "unknown"),
        actor,
        target,
    )
