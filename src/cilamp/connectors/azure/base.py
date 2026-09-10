"""Provider boundary for Azure resource authorization discovery."""

from __future__ import annotations

from typing import Protocol

from cilamp.connectors.azure.models import AzureSnapshot


class AzureConnectorError(RuntimeError):
    """A display-safe ARM connector failure."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class AzureConnector(Protocol):
    mode: str

    def check_connection(self) -> str: ...

    def read_snapshot(self) -> AzureSnapshot: ...
