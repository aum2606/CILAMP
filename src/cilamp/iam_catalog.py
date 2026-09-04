"""Authoritative Phase 1 RBAC catalog for the fictional enterprise."""

from __future__ import annotations

from cilamp.domain import Application, Department, JobRole, Permission


DEPARTMENTS = tuple(
    Department(name)
    for name in ("Engineering", "Finance", "HR", "Sales", "IT", "Marketing")
)

APPLICATIONS = (
    Application("Internal Portal", "Standard"),
    Application("GitHub", "Standard"),
    Application("Jira", "Standard"),
    Application("CRM", "Confidential"),
    Application("HR Portal", "Restricted"),
    Application("Finance Portal", "Restricted"),
    Application("Azure Portal", "Privileged"),
    Application("AWS Console", "Privileged"),
    Application("Marketing Hub", "Standard"),
    Application("Security Center", "Privileged"),
)

PERMISSIONS = (
    Permission("internal.read", "Read company internal content"),
    Permission("source.read_write", "Contribute to approved source repositories"),
    Permission("issues.manage", "Create and manage work items"),
    Permission("engineering.reports", "Read engineering team reports"),
    Permission("finance.read", "Read approved finance records"),
    Permission("finance.approve", "Approve finance workflows"),
    Permission("hr.manage", "Administer employee records"),
    Permission("crm.use", "Work with assigned customer records"),
    Permission("crm.reports", "Read sales performance reports"),
    Permission("cloud.dev.read", "Read approved development cloud resources"),
    Permission("cloud.ops.scoped", "Administer approved infrastructure scopes"),
    Permission("security.audit", "Review identity and security telemetry"),
    Permission("marketing.manage", "Manage campaigns and approved content"),
    Permission(
        "platform.administrator",
        "Simulated unrestricted administrator permission; never assigned by a standard role",
    ),
)

ROLES = (
    JobRole(
        "Developer", "Engineering",
        ("All Employees", "Engineering", "Developers"),
        ("Internal Portal", "GitHub", "Jira", "Azure Portal", "AWS Console"),
        ("internal.read", "source.read_write", "issues.manage", "cloud.dev.read"),
    ),
    JobRole(
        "Engineering Manager", "Engineering",
        ("All Employees", "Engineering", "People Managers"),
        ("Internal Portal", "GitHub", "Jira", "Azure Portal"),
        ("internal.read", "source.read_write", "issues.manage", "engineering.reports", "cloud.dev.read"),
    ),
    JobRole(
        "Finance Analyst", "Finance",
        ("All Employees", "Finance"),
        ("Internal Portal", "Finance Portal"),
        ("internal.read", "finance.read"),
    ),
    JobRole(
        "Finance Manager", "Finance",
        ("All Employees", "Finance", "Finance Approvers", "People Managers"),
        ("Internal Portal", "Finance Portal"),
        ("internal.read", "finance.read", "finance.approve"),
    ),
    JobRole(
        "HR Administrator", "HR",
        ("All Employees", "HR", "HR Administrators"),
        ("Internal Portal", "HR Portal"),
        ("internal.read", "hr.manage"),
        privileged=True,
    ),
    JobRole(
        "Sales User", "Sales",
        ("All Employees", "Sales"),
        ("Internal Portal", "CRM"),
        ("internal.read", "crm.use"),
    ),
    JobRole(
        "Sales Manager", "Sales",
        ("All Employees", "Sales", "People Managers"),
        ("Internal Portal", "CRM"),
        ("internal.read", "crm.use", "crm.reports"),
    ),
    JobRole(
        "IT Administrator", "IT",
        ("All Employees", "IT", "IT Administrators"),
        ("Internal Portal", "Jira", "Azure Portal", "AWS Console"),
        ("internal.read", "issues.manage", "cloud.ops.scoped"),
        privileged=True,
    ),
    JobRole(
        "Security Administrator", "IT",
        ("All Employees", "IT", "Security Administrators"),
        ("Internal Portal", "Security Center", "Azure Portal", "AWS Console"),
        ("internal.read", "security.audit"),
        privileged=True,
    ),
    JobRole(
        "Marketing User", "Marketing",
        ("All Employees", "Marketing"),
        ("Internal Portal", "Marketing Hub"),
        ("internal.read", "marketing.manage"),
    ),
)

ROLE_BY_NAME = {role.name: role for role in ROLES}
DEPARTMENT_NAMES = tuple(department.name for department in DEPARTMENTS)
ROLE_NAMES = tuple(role.name for role in ROLES)
GROUP_NAMES = tuple(sorted({group for role in ROLES for group in role.groups}))


def roles_for_department(department: str) -> tuple[JobRole, ...]:
    return tuple(role for role in ROLES if role.department == department)


def access_matrix_rows() -> list[dict[str, str]]:
    return [
        {
            "Department": role.department,
            "Job Role": role.name,
            "Groups": ", ".join(role.groups),
            "Applications": ", ".join(role.applications),
            "Permissions": ", ".join(role.permissions),
            "Privileged": "Yes" if role.privileged else "No",
        }
        for role in ROLES
    ]
