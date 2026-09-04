import json
from io import BytesIO
from urllib.error import HTTPError

import pytest

from cilamp.connectors.entra import EntraConnectorError
from cilamp.connectors.entra.graph import MicrosoftGraphConnector


class _Token:
    token = "eyJhbGciOiJub25lIn0.eyJ0aWQiOiJsYWItdGVuYW50In0.test-signature"


class FakeCredential:
    def get_token(self, scope, **kwargs):
        assert scope == "https://graph.microsoft.com/.default"
        assert kwargs["tenant_id"] == "lab-tenant"
        return _Token()


class FakeResponse:
    def __init__(self, payload=None):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def read(self):
        return json.dumps(self.payload).encode() if self.payload is not None else b""


def test_graph_connector_uses_v1_endpoints_and_maps_safe_fields() -> None:
    requests = []
    responses = {
        "/users?$select=id&$top=1": {"value": [{"id": "u1"}]},
        "/users?$select=id,displayName,userPrincipalName,accountEnabled,department,jobTitle&$top=999": {
            "value": [
                {
                    "id": "u1",
                    "displayName": "Lab User",
                    "userPrincipalName": "user@lab.example",
                    "accountEnabled": True,
                    "department": "Engineering",
                    "jobTitle": "Developer",
                }
            ]
        },
        "/groups?$select=id,displayName,description,securityEnabled,groupTypes&$top=999": {
            "value": [{"id": "g1", "displayName": "Developers", "securityEnabled": True}]
        },
        "/servicePrincipals?$select=id,displayName,appId,servicePrincipalType,accountEnabled&$top=999": {
            "value": [{"id": "s1", "displayName": "GitHub", "appId": "a1"}]
        },
        "/auditLogs/directoryAudits?$top=25&$orderby=activityDateTime%20desc": {
            "value": []
        },
    }

    def opener(request, timeout):
        assert timeout == 20
        assert request.headers["Authorization"] == f"Bearer {_Token.token}"
        path = request.full_url.removeprefix("https://graph.microsoft.com/v1.0")
        requests.append((request.method, path, request.data))
        return FakeResponse(responses.get(path))

    connector = MicrosoftGraphConnector(
        "lab-tenant", credential=FakeCredential(), opener=opener
    )

    assert connector.check_connection() == "CONNECTED"
    snapshot = connector.read_snapshot()
    connector.update_user("u1", department="IT", job_title="Administrator")
    connector.add_group_member("g1", "u1")
    connector.remove_group_member("g1", "u1")

    assert snapshot.users[0].user_principal_name == "user@lab.example"
    assert snapshot.groups[0].display_name == "Developers"
    assert snapshot.service_principals[0].application_id == "a1"
    assert ("PATCH", "/users/u1") in [(method, path) for method, path, _ in requests]
    assert ("POST", "/groups/g1/members/$ref") in [
        (method, path) for method, path, _ in requests
    ]
    assert ("DELETE", "/groups/g1/members/u1/$ref") in [
        (method, path) for method, path, _ in requests
    ]
    assert _Token.token not in repr(snapshot)


def test_graph_error_is_sanitized_and_does_not_expose_response_or_token() -> None:
    response_body = BytesIO(
        json.dumps(
            {
                "error": {
                    "code": "Authorization_RequestDenied",
                    "message": "sensitive-provider-detail",
                }
            }
        ).encode()
    )

    def denied(request, timeout):
        raise HTTPError(request.full_url, 403, "Forbidden", {}, response_body)

    connector = MicrosoftGraphConnector(
        "lab-tenant", credential=FakeCredential(), opener=denied
    )

    with pytest.raises(EntraConnectorError) as captured:
        connector.check_connection()

    message = str(captured.value)
    assert "HTTP 403 Authorization_RequestDenied" in message
    assert "sensitive-provider-detail" not in message
    assert _Token.token not in message


def test_graph_connector_rejects_token_from_another_tenant() -> None:
    class WrongTenantToken:
        token = "eyJhbGciOiJub25lIn0.eyJ0aWQiOiJvdGhlci10ZW5hbnQifQ.signature"

    class WrongTenantCredential:
        def get_token(self, scope, **kwargs):
            return WrongTenantToken()

    connector = MicrosoftGraphConnector(
        "lab-tenant", credential=WrongTenantCredential(), opener=lambda *args: None
    )

    with pytest.raises(EntraConnectorError, match="different tenant"):
        connector.check_connection()
