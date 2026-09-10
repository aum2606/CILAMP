from datetime import datetime, timezone

import pytest

from cilamp.connectors.aws import AwsConnectorError
from cilamp.connectors.aws.boto import BotoAwsConnector


class Paginator:
    def __init__(self, response): self.response = response
    def paginate(self, **kwargs): return [self.response]


class Client:
    def __init__(self, calls, responses): self.calls, self.responses = calls, responses
    def get_paginator(self, method):
        self.calls.append((method, {}))
        return Paginator(self.responses[method])
    def __getattr__(self, method):
        def call(**kwargs):
            self.calls.append((method, kwargs))
            response = self.responses[method]
            if isinstance(response, Exception): raise response
            return response
        return call


class Session:
    def __init__(self, clients): self.clients = clients
    def client(self, service, region_name): return self.clients[service]


def _session(caller_arn="arn:aws:sts::123456789012:assumed-role/CILAMP-Audit/test"):
    calls=[]
    role_arn="arn:aws:iam::123456789012:role/cilamp/CILAMP-DeveloperRole"
    policy_arn="arn:aws:iam::123456789012:policy/cilamp/DeveloperRead"
    clients={
        "sts": Client(calls,{"get_caller_identity":{"Account":"123456789012","Arn":caller_arn}}),
        "iam": Client(calls,{"list_roles":{"Roles":[{"Arn":role_arn,"RoleName":"CILAMP-DeveloperRole","Path":"/cilamp/","AssumeRolePolicyDocument":{"Statement":[{"Principal":{"Federated":"identity-center"}}]}}]},"list_attached_role_policies":{"AttachedPolicies":[{"PolicyArn":policy_arn,"PolicyName":"DeveloperRead"}]},"get_policy":{"Policy":{"DefaultVersionId":"v1"}},"get_policy_version":{"PolicyVersion":{"Document":{"Statement":[{"Effect":"Allow","Action":"s3:GetObject","Resource":"arn:aws:s3:::lab/*"}]}}},"list_role_policies":{"PolicyNames":[]}}),
        "s3": Client(calls,{"head_bucket":{}}),
        "cloudtrail": Client(calls,{"lookup_events":{"Events":[{"EventId":"event-1","EventTime":datetime(2026,1,1,tzinfo=timezone.utc),"EventName":"AssumeRole","Username":"tester","Resources":[]}]}}),
    }
    return Session(clients), calls


def test_boto_connector_is_scoped_read_only_and_caches_no_credentials() -> None:
    session,calls=_session()
    connector=BotoAwsConnector("123456789012","ap-south-1","/cilamp/",("lab",),session=session)
    assert connector.check_connection()=="CONNECTED"
    snapshot=connector.read_snapshot()
    assert snapshot.roles[0].trusted_principals == ("identity-center",)
    assert snapshot.policies[0].statements[0].actions == ("s3:GetObject",)
    assert len(snapshot.resources) == 2
    assert all(not method.startswith(("create","delete","put","update","attach","detach")) for method,_ in calls)


def test_boto_connector_rejects_root_credentials() -> None:
    session,_=_session("arn:aws:iam::123456789012:root")
    with pytest.raises(AwsConnectorError, match="root credentials"):
        BotoAwsConnector("123456789012","ap-south-1","/cilamp/",(),session=session).check_connection()


def test_boto_connector_rejects_wrong_account() -> None:
    session,_=_session()
    with pytest.raises(AwsConnectorError, match="different account"):
        BotoAwsConnector("999999999999","ap-south-1","/cilamp/",(),session=session).check_connection()
