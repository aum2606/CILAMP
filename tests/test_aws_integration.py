from pathlib import Path

import pytest

from cilamp.aws_policy import evaluate_aws_access
from cilamp.aws_repository import get_aws_sync_state, initialize_aws_store, list_aws_bindings, list_aws_cloudtrail_events, list_aws_operations, list_aws_policies, list_aws_resources, list_aws_roles
from cilamp.aws_service import AwsSafetyError, aws_connector_for, synchronize_aws
from cilamp.config import Settings
from cilamp.repository import initialize_organization


@pytest.fixture
def settings():
    path = Path(__file__).parents[1] / "data" / "test-aws.db"
    path.unlink(missing_ok=True)
    initialize_organization(path)
    initialize_aws_store(path)
    yield Settings(mode="SIMULATION", database_path=path)
    path.unlink(missing_ok=True)


def test_simulation_sync_persists_iam_s3_sts_and_cloudtrail(settings) -> None:
    correlation_id = synchronize_aws(settings)
    state = get_aws_sync_state(settings.database_path)
    assert correlation_id and state.status == "CONNECTED"
    assert (state.resource_count, state.role_count, state.policy_count, state.event_count) == (4, 3, 3, 2)
    assert len(list_aws_cloudtrail_events(settings.database_path)) == 2
    assert list_aws_operations(settings.database_path)[0].result == "SUCCESS"


def test_cached_aws_snapshot_evaluates_effective_access(settings) -> None:
    synchronize_aws(settings)
    role = next(x for x in list_aws_roles(settings.database_path) if x.name == "CILAMP-DeveloperRole")
    resource = next(x for x in list_aws_resources(settings.database_path) if x.name == "onboarding-guide.pdf")
    decision = evaluate_aws_access(role, resource, "s3:GetObject", list_aws_policies(settings.database_path), list_aws_bindings(settings.database_path))
    assert decision.decision == "ALLOWED"


def test_live_connector_requires_aws_specific_guard(settings) -> None:
    live = Settings(mode="LIVE_LAB", database_path=settings.database_path, entra_lab_enabled=True, entra_tenant_id="lab", aws_lab_enabled=False)
    with pytest.raises(AwsSafetyError, match="disabled"):
        aws_connector_for(live)
