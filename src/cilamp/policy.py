"""Provider-independent RBAC and least-privilege evaluation."""

from __future__ import annotations

from cilamp.domain import (
    AccessFinding,
    AccessReview,
    EffectiveAccess,
    Employee,
    EmployeeStatus,
    RiskLevel,
)
from cilamp.iam_catalog import ROLE_BY_NAME


PRIVILEGED_PERMISSIONS = {"platform.administrator", "cloud.ops.scoped"}
PRIVILEGED_GROUPS = {"IT Administrators", "Security Administrators", "HR Administrators"}
PRIVILEGED_APPLICATIONS = {"Security Center"}


def expected_access(employee: Employee) -> EffectiveAccess:
    """Calculate policy-approved access for the identity's current state."""

    if employee.status == EmployeeStatus.DISABLED:
        return EffectiveAccess((), (), ())
    role = ROLE_BY_NAME[employee.job_role]
    return EffectiveAccess(
        tuple(sorted(role.groups)),
        tuple(sorted(role.applications)),
        tuple(sorted(role.permissions)),
    )


def evaluate_access(employee: Employee, actual: EffectiveAccess) -> AccessReview:
    expected = expected_access(employee)
    normalized_actual = EffectiveAccess(
        tuple(sorted(actual.groups)),
        tuple(sorted(actual.applications)),
        tuple(sorted(actual.permissions)),
    )
    findings: list[AccessFinding] = []

    _evaluate_excess(
        findings,
        "GROUP",
        set(normalized_actual.groups) - set(expected.groups),
        PRIVILEGED_GROUPS,
    )
    _evaluate_excess(
        findings,
        "APPLICATION",
        set(normalized_actual.applications) - set(expected.applications),
        PRIVILEGED_APPLICATIONS,
    )
    _evaluate_excess(
        findings,
        "PERMISSION",
        set(normalized_actual.permissions) - set(expected.permissions),
        PRIVILEGED_PERMISSIONS,
    )

    _evaluate_missing(
        findings, "GROUP", set(expected.groups) - set(normalized_actual.groups)
    )
    _evaluate_missing(
        findings,
        "APPLICATION",
        set(expected.applications) - set(normalized_actual.applications),
    )
    _evaluate_missing(
        findings,
        "PERMISSION",
        set(expected.permissions) - set(normalized_actual.permissions),
    )

    role = ROLE_BY_NAME[employee.job_role]
    privileged = (employee.status == EmployeeStatus.ACTIVE and role.privileged) or bool(
        set(normalized_actual.permissions) & PRIVILEGED_PERMISSIONS
        or set(normalized_actual.groups) & PRIVILEGED_GROUPS
        or set(normalized_actual.applications) & PRIVILEGED_APPLICATIONS
    )
    return AccessReview(
        employee=employee,
        expected=expected,
        actual=normalized_actual,
        findings=tuple(findings),
        privileged=privileged,
    )


def _evaluate_excess(
    findings: list[AccessFinding],
    entitlement_type: str,
    entitlements: set[str],
    privileged_entitlements: set[str],
) -> None:
    for entitlement in sorted(entitlements):
        if entitlement in privileged_entitlements:
            findings.append(
                AccessFinding(
                    category="EXCESSIVE_PRIVILEGE",
                    risk=RiskLevel.CRITICAL,
                    entitlement_type=entitlement_type,
                    entitlement=entitlement,
                    explanation=(
                        "Privileged access is present but is not authorized by the employee's "
                        "current role."
                    ),
                    suggested_remediation="Remove the privileged assignment immediately and review its origin.",
                )
            )
        elif entitlement_type == "PERMISSION":
            findings.append(
                AccessFinding(
                    category="PRIVILEGE_CREEP",
                    risk=RiskLevel.HIGH,
                    entitlement_type=entitlement_type,
                    entitlement=entitlement,
                    explanation=(
                        "This permission is not expected for the current role and may be stale "
                        "access retained from an earlier assignment."
                    ),
                    suggested_remediation="Remove the stale permission unless an approved exception exists.",
                )
            )
        else:
            findings.append(
                AccessFinding(
                    category="UNAUTHORIZED_ACCESS",
                    risk=RiskLevel.HIGH,
                    entitlement_type=entitlement_type,
                    entitlement=entitlement,
                    explanation="The assignment is outside the employee's approved role baseline.",
                    suggested_remediation="Remove the unauthorized assignment or document an exception.",
                )
            )


def _evaluate_missing(
    findings: list[AccessFinding], entitlement_type: str, entitlements: set[str]
) -> None:
    for entitlement in sorted(entitlements):
        findings.append(
            AccessFinding(
                category="MISSING_ACCESS",
                risk=RiskLevel.MEDIUM,
                entitlement_type=entitlement_type,
                entitlement=entitlement,
                explanation="Required role access is absent and may prevent the employee from working.",
                suggested_remediation="Restore the role-approved assignment after validating the identity.",
            )
        )


def access_source_rows(review: AccessReview) -> list[dict[str, str]]:
    """Explain how effective access relates to role/group policy or direct variance."""

    rows: list[dict[str, str]] = []
    expected_by_type = {
        "GROUP": set(review.expected.groups),
        "APPLICATION": set(review.expected.applications),
        "PERMISSION": set(review.expected.permissions),
    }
    actual_by_type = {
        "GROUP": review.actual.groups,
        "APPLICATION": review.actual.applications,
        "PERMISSION": review.actual.permissions,
    }
    for entitlement_type, entitlements in actual_by_type.items():
        for entitlement in entitlements:
            approved = entitlement in expected_by_type[entitlement_type]
            rows.append(
                {
                    "Type": entitlement_type.title(),
                    "Entitlement": entitlement,
                    "Source": (
                        f"Inherited through {review.employee.job_role} role/group policy"
                        if approved
                        else "Direct or stale assignment outside role policy"
                    ),
                    "Policy": "EXPECTED" if approved else "UNAUTHORIZED",
                }
            )
    return rows
