"""Read-only boto3 adapter restricted to a dedicated AWS lab inventory."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from urllib.parse import unquote

from cilamp.connectors.aws.base import AwsConnectorError
from cilamp.connectors.aws.models import AwsCloudTrailEvent, AwsPolicy, AwsPolicyStatement, AwsResource, AwsRole, AwsRolePolicyBinding, AwsSnapshot


class BotoAwsConnector:
    """Use only STS and read/list APIs; no mutation method is exposed."""

    mode = "LIVE_LAB"

    def __init__(self, account_id: str, region: str, role_path: str, bucket_names: tuple[str, ...], profile: str = "", *, session=None) -> None:
        if not (account_id.isdigit() and len(account_id) == 12):
            raise ValueError("A 12-digit dedicated lab AWS account ID is required.")
        if role_path == "/" or not role_path.startswith("/") or not role_path.endswith("/"):
            raise ValueError("AWS role path must be a non-root path that starts and ends with '/'.")
        self.account_id, self.region, self.role_path = account_id, region, role_path
        self.bucket_names, self.profile = bucket_names, profile
        if session is None:
            try:
                import boto3
                session = boto3.Session(profile_name=profile or None, region_name=region)
            except Exception as error:
                raise AwsConnectorError(f"AWS SDK session could not be created ({type(error).__name__}).") from error
        self.session = session
        self.identity: dict[str, Any] | None = None

    def _client(self, service: str):
        try:
            return self.session.client(service, region_name=self.region)
        except Exception as error:
            raise AwsConnectorError(f"AWS {service} client could not be created ({type(error).__name__}).") from error

    @staticmethod
    def _error(method: str, error: Exception) -> AwsConnectorError:
        code = getattr(error, "response", {}).get("Error", {}).get("Code", type(error).__name__)
        return AwsConnectorError(f"AWS read-only {method} failed ({code}). Verify dedicated-lab read permissions.")

    def _call(self, client, method: str, **kwargs):
        try:
            return getattr(client, method)(**kwargs)
        except Exception as error:
            raise self._error(method, error) from error

    def _items(self, client, method: str, key: str, **kwargs) -> list[Any]:
        try:
            pages = client.get_paginator(method).paginate(**kwargs)
            return [item for index, page in enumerate(pages) if index < 10 for item in page.get(key, [])]
        except Exception as error:
            raise self._error(method, error) from error

    def check_connection(self) -> str:
        self.identity = self._call(self._client("sts"), "get_caller_identity")
        if self.identity.get("Account") != self.account_id:
            raise AwsConnectorError("Authenticated AWS identity belongs to a different account than the configured lab.")
        if self.identity.get("Arn", "").endswith(":root"):
            raise AwsConnectorError("AWS root credentials are prohibited. Use a least-privileged role or SSO profile.")
        return "CONNECTED"

    def read_snapshot(self) -> AwsSnapshot:
        if self.identity is None:
            self.check_connection()
        iam = self._client("iam")
        roles, policies, bindings, limitations = [], {}, [], []
        for item in self._items(iam, "list_roles", "Roles", PathPrefix=self.role_path):
            role = AwsRole(item["Arn"], item["RoleName"], item.get("Path", "/"), _trust_principals(item.get("AssumeRolePolicyDocument", {})), "IAM_ROLE_STS_NO_STORED_KEYS")
            roles.append(role)
            for attached in self._items(iam, "list_attached_role_policies", "AttachedPolicies", RoleName=role.name):
                arn = attached["PolicyArn"]
                detail = self._call(iam, "get_policy", PolicyArn=arn)["Policy"]
                version = self._call(iam, "get_policy_version", PolicyArn=arn, VersionId=detail["DefaultVersionId"])["PolicyVersion"]
                statements, conditional = _statements(version.get("Document", {}))
                policies[arn] = AwsPolicy(arn, attached["PolicyName"], "AWS_MANAGED" if arn.startswith("arn:aws:iam::aws:") else "CUSTOMER_MANAGED", statements)
                bindings.append(AwsRolePolicyBinding(role.arn, arn))
                if conditional:
                    limitations.append(f"Policy {attached['PolicyName']} contains conditions or inverse fields; cached evaluation may be UNKNOWN.")
            for name in self._items(iam, "list_role_policies", "PolicyNames", RoleName=role.name):
                response = self._call(iam, "get_role_policy", RoleName=role.name, PolicyName=name)
                arn = f"{role.arn}/inline-policy/{name}"
                statements, conditional = _statements(response.get("PolicyDocument", {}))
                policies[arn] = AwsPolicy(arn, name, "INLINE", statements)
                bindings.append(AwsRolePolicyBinding(role.arn, arn))
                if conditional:
                    limitations.append(f"Inline policy {name} contains conditions or inverse fields; cached evaluation may be UNKNOWN.")
        resources = []
        s3 = self._client("s3")
        for bucket in self.bucket_names:
            self._call(s3, "head_bucket", Bucket=bucket)
            resources.append(AwsResource(f"arn:aws:s3:::{bucket}", bucket, "S3 bucket", "global"))
            resources.append(AwsResource(f"arn:aws:s3:::{bucket}/*", f"{bucket} object scope", "S3 object scope", "global"))
        events = []
        try:
            response = self._call(self._client("cloudtrail"), "lookup_events", MaxResults=25)
            for event in response.get("Events", []):
                names = [resource.get("ResourceName", "") for resource in event.get("Resources", [])]
                events.append(AwsCloudTrailEvent(event.get("EventId", ""), event.get("EventTime") or datetime.now(timezone.utc), event.get("EventName", "Unknown"), event.get("Username", ""), ", ".join(filter(None, names))))
        except AwsConnectorError as error:
            limitations.append(f"CloudTrail lookup unavailable: {error}")
        limitations.insert(0, "Cached identity-policy evaluation excludes resource policies, SCPs/RCPs, permissions boundaries, session policies, tags, and request context.")
        return AwsSnapshot(tuple(resources), tuple(roles), tuple(policies.values()), tuple(bindings), tuple(events), self.identity.get("Arn", ""), tuple(dict.fromkeys(limitations)))


def _sequence(value: Any) -> tuple[str, ...]:
    return (value,) if isinstance(value, str) else tuple(str(item) for item in (value or ()))


def _document(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        return json.loads(unquote(value))
    return value if isinstance(value, dict) else {}


def _statements(document: Any) -> tuple[tuple[AwsPolicyStatement, ...], bool]:
    raw = _document(document).get("Statement", [])
    raw = [raw] if isinstance(raw, dict) else raw
    statements = tuple(AwsPolicyStatement(item.get("Sid", ""), item.get("Effect", "Unknown"), _sequence(item.get("Action") or ("*" if item.get("NotAction") else ())), _sequence(item.get("Resource") or ("*" if item.get("NotResource") else "*")), bool(item.get("Condition") or item.get("NotAction") or item.get("NotResource"))) for item in raw)
    return statements, any(statement.has_conditions for statement in statements)


def _trust_principals(document: Any) -> tuple[str, ...]:
    principals = []
    statements = _document(document).get("Statement", [])
    statements = [statements] if isinstance(statements, dict) else statements
    for statement in statements:
        principal = statement.get("Principal", {})
        if isinstance(principal, str):
            principals.append(principal)
        elif isinstance(principal, dict):
            for value in principal.values():
                principals.extend(_sequence(value))
    return tuple(dict.fromkeys(principals))
