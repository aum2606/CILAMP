"""Safe orchestration for AWS IAM discovery."""

from cilamp.aws_repository import initialize_aws_store, mark_aws_failure, record_aws_operation, save_aws_snapshot
from cilamp.config import Settings
from cilamp.connectors.aws import AwsConnector, AwsConnectorError, BotoAwsConnector, SimulationAwsConnector


class AwsSafetyError(RuntimeError):
    """Raised when live AWS configuration is incomplete or unsafe."""


def aws_connector_for(settings: Settings) -> AwsConnector:
    if settings.mode == "SIMULATION":
        return SimulationAwsConnector()
    if not settings.aws_lab_enabled:
        raise AwsSafetyError("AWS LIVE_LAB access is disabled; enable only a dedicated AWS lab.")
    return BotoAwsConnector(settings.aws_account_id, settings.aws_region, settings.aws_role_path, settings.aws_allowed_buckets, settings.aws_profile)


def synchronize_aws(settings: Settings, connector: AwsConnector | None=None) -> str:
    initialize_aws_store(settings.database_path)
    connector=connector or aws_connector_for(settings)
    try:
        connector.check_connection()
        snapshot=connector.read_snapshot()
        save_aws_snapshot(settings.database_path,snapshot,settings.mode,settings.aws_account_label,settings.aws_region)
        return record_aws_operation(settings.database_path,settings.mode,"AWS_IAM_SYNCHRONIZATION",settings.aws_account_label,"SUCCESS",f"Cached {len(snapshot.roles)} roles, {len(snapshot.policies)} policies, {len(snapshot.resources)} resources, and {len(snapshot.cloudtrail_events)} CloudTrail events.")
    except AwsConnectorError as error:
        mark_aws_failure(settings.database_path,settings.mode,settings.aws_account_label,settings.aws_region,str(error))
        record_aws_operation(settings.database_path,settings.mode,"AWS_IAM_SYNCHRONIZATION",settings.aws_account_label,"FAILURE",str(error))
        raise
