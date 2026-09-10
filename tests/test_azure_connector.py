import json
from io import BytesIO
from urllib.error import HTTPError

import pytest

from cilamp.connectors.azure import AzureConnectorError
from cilamp.connectors.azure.arm import AzureResourceManagerConnector


class Token:
    token = "eyJhbGciOiJub25lIn0.eyJ0aWQiOiJsYWItdGVuYW50In0.signature"


class Credential:
    def get_token(self, scope, **kwargs):
        assert scope == "https://management.azure.com/.default"
        assert kwargs["tenant_id"] == "lab-tenant"
        return Token()


class Response:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return json.dumps(self.payload).encode()


def test_arm_connector_reads_scoped_resources_identities_and_assignments() -> None:
    prefix = "/subscriptions/lab-subscription/resourceGroups/rg-lab"
    role_id = "/subscriptions/lab-subscription/providers/Microsoft.Authorization/roleDefinitions/role-1"
    responses = {
        f"{prefix}?api-version=2021-04-01": {"id": prefix},
        f"{prefix}/resources?api-version=2021-04-01": {
            "value": [
                {
                    "id": f"{prefix}/providers/Microsoft.Storage/storageAccounts/store1",
                    "name": "store1",
                    "type": "Microsoft.Storage/storageAccounts",
                    "location": "centralindia",
                    "identity": {"type": "SystemAssigned", "principalId": "principal-1"},
                }
            ]
        },
        f"{prefix}/providers/Microsoft.ManagedIdentity/userAssignedIdentities?api-version=2023-01-31": {
            "value": []
        },
        f"{prefix}/providers/Microsoft.Authorization/roleDefinitions?api-version=2022-04-01": {
            "value": [{"id": role_id, "properties": {"roleName": "Storage Blob Data Reader"}}]
        },
        f"{prefix}/providers/Microsoft.Authorization/roleAssignments?api-version=2022-04-01": {
            "value": [
                {
                    "id": "assignment-1",
                    "properties": {
                        "principalId": "principal-1",
                        "principalType": "ServicePrincipal",
                        "roleDefinitionId": role_id,
                        "scope": f"{prefix}/providers/Microsoft.Storage/storageAccounts/store1",
                    },
                }
            ]
        },
    }
    requests = []

    def opener(request, timeout):
        assert timeout == 20
        assert request.headers["Authorization"] == f"Bearer {Token.token}"
        path = request.full_url.removeprefix("https://management.azure.com")
        requests.append(path)
        return Response(responses[path])

    connector = AzureResourceManagerConnector(
        "lab-tenant",
        "lab-subscription",
        "rg-lab",
        credential=Credential(),
        opener=opener,
    )

    assert connector.check_connection() == "CONNECTED"
    snapshot = connector.read_snapshot()

    assert len(snapshot.resources) == 2
    assert snapshot.identities[0].credential_mode == "MANAGED_IDENTITY_NO_STORED_SECRET"
    assert snapshot.role_assignments[0].role_name == "Storage Blob Data Reader"
    assert all(path.startswith("/subscriptions/lab-subscription") for path in requests)
    assert Token.token not in repr(snapshot)


def test_arm_connector_rejects_wrong_tenant_token() -> None:
    class WrongToken:
        token = "eyJhbGciOiJub25lIn0.eyJ0aWQiOiJvdGhlciJ9.signature"

    class WrongCredential:
        def get_token(self, *args, **kwargs):
            return WrongToken()

    connector = AzureResourceManagerConnector(
        "lab-tenant", "lab-sub", "rg-lab", credential=WrongCredential()
    )
    with pytest.raises(AzureConnectorError, match="different tenant"):
        connector.check_connection()


def test_arm_error_hides_provider_detail_and_token() -> None:
    body = BytesIO(
        json.dumps(
            {"error": {"code": "AuthorizationFailed", "message": "private-detail"}}
        ).encode()
    )

    def denied(request, timeout):
        raise HTTPError(request.full_url, 403, "Forbidden", {}, body)

    connector = AzureResourceManagerConnector(
        "lab-tenant", "lab-sub", "rg-lab", credential=Credential(), opener=denied
    )
    with pytest.raises(AzureConnectorError) as captured:
        connector.check_connection()
    message = str(captured.value)
    assert "HTTP 403 AuthorizationFailed" in message
    assert "private-detail" not in message
    assert Token.token not in message


def test_arm_invalid_json_is_reported_without_response_content() -> None:
    class InvalidResponse(Response):
        def read(self):
            return b"sensitive-non-json-response"

    connector = AzureResourceManagerConnector(
        "lab-tenant",
        "lab-sub",
        "rg-lab",
        credential=Credential(),
        opener=lambda request, timeout: InvalidResponse(None),
    )

    with pytest.raises(AzureConnectorError) as captured:
        connector.check_connection()

    assert "invalid JSON" in str(captured.value)
    assert "sensitive-non-json-response" not in str(captured.value)
