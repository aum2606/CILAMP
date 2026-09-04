"""Provider boundary for Microsoft Entra operations."""

from __future__ import annotations

from typing import Protocol

from cilamp.connectors.entra.models import EntraSnapshot, EntraUser


class EntraConnectorError(RuntimeError):
    """A display-safe connector failure without tokens or response bodies."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class EntraConnector(Protocol):
    mode: str

    def check_connection(self) -> str: ...

    def read_snapshot(self) -> EntraSnapshot: ...

    def list_group_members(self, group_id: str) -> tuple[EntraUser, ...]: ...

    def update_user(
        self, user_id: str, *, department: str, job_title: str
    ) -> None: ...

    def add_group_member(self, group_id: str, user_id: str) -> None: ...

    def remove_group_member(self, group_id: str, user_id: str) -> None: ...
