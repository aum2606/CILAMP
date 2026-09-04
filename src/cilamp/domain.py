"""Provider-independent identity and access domain objects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EmployeeStatus(StrEnum):
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


@dataclass(frozen=True)
class Department:
    name: str


@dataclass(frozen=True)
class Group:
    name: str


@dataclass(frozen=True)
class Application:
    name: str
    sensitivity: str


@dataclass(frozen=True)
class Permission:
    name: str
    description: str


@dataclass(frozen=True)
class JobRole:
    name: str
    department: str
    groups: tuple[str, ...]
    applications: tuple[str, ...]
    permissions: tuple[str, ...]
    privileged: bool = False


@dataclass(frozen=True)
class Employee:
    employee_id: str
    display_name: str
    email: str
    department: str
    job_role: str
    status: EmployeeStatus = EmployeeStatus.ACTIVE


@dataclass(frozen=True)
class EffectiveAccess:
    groups: tuple[str, ...]
    applications: tuple[str, ...]
    permissions: tuple[str, ...]
