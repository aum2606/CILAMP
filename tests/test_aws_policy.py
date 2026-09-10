import pytest

from cilamp.aws_policy import evaluate_aws_access
from cilamp.connectors.aws.simulation import SimulationAwsConnector
from cilamp.connectors.aws.models import AwsPolicy, AwsPolicyStatement, AwsRolePolicyBinding


def _items():
    snapshot = SimulationAwsConnector().read_snapshot()
    role = next(x for x in snapshot.roles if x.name == "CILAMP-DeveloperRole")
    obj = next(x for x in snapshot.resources if x.name == "onboarding-guide.pdf")
    return snapshot, role, obj


def test_developer_can_read_only_selected_development_objects() -> None:
    snapshot, role, obj = _items()
    allowed = evaluate_aws_access(role, obj, "s3:GetObject", snapshot.policies, snapshot.bindings)
    denied = evaluate_aws_access(role, obj, "s3:DeleteObject", snapshot.policies, snapshot.bindings)
    admin = evaluate_aws_access(role, obj, "iam:CreateUser", snapshot.policies, snapshot.bindings)

    assert allowed.decision == "ALLOWED"
    assert denied.decision == "EXPLICIT DENY"
    assert admin.decision == "NOT GRANTED"


def test_unsupported_action_is_rejected() -> None:
    snapshot, role, obj = _items()
    with pytest.raises(ValueError, match="Unsupported AWS action"):
        evaluate_aws_access(role, obj, "aws:Anything", snapshot.policies, snapshot.bindings)


def test_explicit_deny_overrides_an_allow_from_another_policy() -> None:
    snapshot, role, obj = _items()
    allow_delete = AwsPolicy("allow-delete", "BroadAllow", "TEST", (AwsPolicyStatement("", "Allow", ("s3:DeleteObject",), ("*",)),))
    decision = evaluate_aws_access(role, obj, "s3:DeleteObject", snapshot.policies + (allow_delete,), snapshot.bindings + (AwsRolePolicyBinding(role.arn, allow_delete.arn),))
    assert decision.decision == "EXPLICIT DENY"


def test_conditional_match_is_unknown_without_request_context() -> None:
    snapshot, role, obj = _items()
    conditional = AwsPolicy("conditional", "ConditionalRead", "TEST", (AwsPolicyStatement("", "Allow", ("s3:GetObject",), ("*",), True),))
    decision = evaluate_aws_access(role, obj, "s3:GetObject", (conditional,), (AwsRolePolicyBinding(role.arn, conditional.arn),))
    assert decision.decision == "UNKNOWN"
