"""Provider boundary for AWS IAM discovery."""

from typing import Protocol

from cilamp.connectors.aws.models import AwsSnapshot


class AwsConnectorError(RuntimeError):
    """A display-safe AWS connector failure."""


class AwsConnector(Protocol):
    mode: str

    def check_connection(self) -> str: ...
    def read_snapshot(self) -> AwsSnapshot: ...
