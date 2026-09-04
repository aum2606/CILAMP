"""Pure definitions and plans for Phase 4 security simulations."""

from __future__ import annotations

from dataclasses import dataclass

from cilamp.domain import (
    AccessChanges,
    EffectiveAccess,
    Employee,
    EmployeeStatus,
    RiskLevel,
    SecurityFinding,
    SecurityScenarioPlan,
)


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario_type: str
    title: str
    purpose: str
    target_rule: str


SCENARIOS = (
    ScenarioDefinition(
        "EXCESSIVE_PRIVILEGE",
        "Developer receives Administrator permission",
        "Detect a critical privilege assignment outside the approved role.",
        "ACTIVE_DEVELOPER",
    ),
    ScenarioDefinition(
        "OLD_DEPARTMENT_ACCESS",
        "Employee retains old department access",
        "Detect Engineering access retained by a Finance employee after a move.",
        "ACTIVE_FINANCE_ANALYST",
    ),
    ScenarioDefinition(
        "DISABLED_WITH_APPLICATION",
        "Disabled employee still has application access",
        "Detect incomplete offboarding where an application remains assigned.",
        "ACTIVE_EMPLOYEE",
    ),
    ScenarioDefinition(
        "UNAUTHORIZED_GROUP",
        "Unauthorized group membership",
        "Detect a Developer placed in the Finance group without role justification.",
        "ACTIVE_DEVELOPER",
    ),
    ScenarioDefinition(
        "INSECURE_WORKLOAD_CREDENTIAL",
        "Workload credential stored insecurely (simulated)",
        "Represent a static source-code credential without storing any credential value.",
        "WORKLOAD",
    ),
    ScenarioDefinition(
        "MISSING_REQUIRED_ACCESS",
        "User cannot access a required application",
        "Detect and troubleshoot a missing GitHub assignment for a Developer.",
        "ACTIVE_DEVELOPER",
    ),
)

SCENARIO_BY_TYPE = {scenario.scenario_type: scenario for scenario in SCENARIOS}


def build_scenario_plan(
    scenario_type: str,
    employee: Employee | None,
    current_access: EffectiveAccess,
) -> SecurityScenarioPlan:
    definition = SCENARIO_BY_TYPE.get(scenario_type)
    if definition is None:
        raise ValueError(f"Unknown security scenario: {scenario_type}")

    if scenario_type == "INSECURE_WORKLOAD_CREDENTIAL":
        if employee is not None:
            raise ValueError("The workload scenario does not target a human employee.")
        return SecurityScenarioPlan(
            scenario_type=scenario_type,
            target_identity="workload:legacy-reporting-app",
            title=definition.title,
            description=definition.purpose,
            risk=RiskLevel.HIGH,
            evidence={
                "identity_type": "WORKLOAD",
                "credential_storage": "SOURCE_CODE (SIMULATED)",
                "secret_value_stored": "NO",
            },
            recommendation=(
                "Remove the static credential and use managed identity, workload identity "
                "federation, or a short-lived role credential."
            ),
            observed_action="WORKLOAD_CREDENTIAL_POSTURE_CHECK",
        )

    if employee is None or employee.status != EmployeeStatus.ACTIVE:
        raise ValueError("Select an active employee for this scenario.")

    if scenario_type == "EXCESSIVE_PRIVILEGE":
        _require_role(employee, "Developer")
        return SecurityScenarioPlan(
            scenario_type=scenario_type,
            target_identity=employee.employee_id,
            title=definition.title,
            description=definition.purpose,
            risk=RiskLevel.CRITICAL,
            evidence={
                "role": employee.job_role,
                "unexpected_permission": "platform.administrator",
            },
            recommendation="Remove Administrator permission and investigate the grant source.",
            to_add=AccessChanges(permissions=("platform.administrator",)),
            observed_action="PRIVILEGED_ACCESS_POLICY_CHECK",
        )

    if scenario_type == "OLD_DEPARTMENT_ACCESS":
        _require_role(employee, "Finance Analyst")
        return SecurityScenarioPlan(
            scenario_type=scenario_type,
            target_identity=employee.employee_id,
            title=definition.title,
            description=definition.purpose,
            risk=RiskLevel.HIGH,
            evidence={
                "current_department": employee.department,
                "retained_department": "Engineering",
                "retained_group": "Developers",
            },
            recommendation="Remove retained Engineering access and validate the Mover audit trail.",
            to_add=AccessChanges(
                groups=("Developers",),
                applications=("GitHub",),
                permissions=("source.read_write",),
            ),
            observed_action="MOVER_ACCESS_REVIEW",
        )

    if scenario_type == "DISABLED_WITH_APPLICATION":
        return SecurityScenarioPlan(
            scenario_type=scenario_type,
            target_identity=employee.employee_id,
            title=definition.title,
            description=definition.purpose,
            risk=RiskLevel.CRITICAL,
            evidence={
                "account_status": "DISABLED",
                "retained_application": "Internal Portal",
            },
            recommendation="Revoke residual application access and review offboarding completeness.",
            to_remove=AccessChanges(
                groups=current_access.groups,
                applications=current_access.applications,
                permissions=current_access.permissions,
            ),
            to_add=AccessChanges(applications=("Internal Portal",)),
            new_status=EmployeeStatus.DISABLED,
            observed_action="OFFBOARDING_COMPLETENESS_CHECK",
        )

    if scenario_type == "UNAUTHORIZED_GROUP":
        _require_role(employee, "Developer")
        return SecurityScenarioPlan(
            scenario_type=scenario_type,
            target_identity=employee.employee_id,
            title=definition.title,
            description=definition.purpose,
            risk=RiskLevel.HIGH,
            evidence={"role": employee.job_role, "unauthorized_group": "Finance"},
            recommendation="Remove the Finance group and verify who approved the membership.",
            to_add=AccessChanges(groups=("Finance",)),
            observed_action="GROUP_MEMBERSHIP_POLICY_CHECK",
        )

    if scenario_type == "MISSING_REQUIRED_ACCESS":
        _require_role(employee, "Developer")
        if "GitHub" not in current_access.applications:
            raise ValueError("The selected Developer already lacks GitHub access.")
        return SecurityScenarioPlan(
            scenario_type=scenario_type,
            target_identity=employee.employee_id,
            title=definition.title,
            description=definition.purpose,
            risk=RiskLevel.MEDIUM,
            evidence={
                "role": employee.job_role,
                "required_application": "GitHub",
                "access_test": "DENIED",
            },
            recommendation="Restore the role-approved GitHub assignment after identity validation.",
            to_remove=AccessChanges(applications=("GitHub",)),
            observed_action="APPLICATION_ACCESS_CHECK",
        )

    raise ValueError(f"Scenario is not implemented: {scenario_type}")


def _require_role(employee: Employee, required_role: str) -> None:
    if employee.job_role != required_role:
        raise ValueError(f"Scenario requires an active {required_role}.")


def troubleshooting_steps(finding: SecurityFinding) -> tuple[str, ...]:
    common = (
        "Confirm the target identity and current status.",
        "Compare expected role access with actual assignments.",
        "Review audit events using the finding correlation ID.",
    )
    scenario_steps = {
        "EXCESSIVE_PRIVILEGE": (
            "Identify the source of the Administrator grant.",
            "Check for other privileged groups, roles, or direct permissions.",
            "Remove access not justified by the current role.",
        ),
        "OLD_DEPARTMENT_ACCESS": (
            "Review the most recent Mover event and its removal set.",
            "Confirm the old department group/application/permission was removed.",
            "Reconcile assignments to the destination-role baseline.",
        ),
        "DISABLED_WITH_APPLICATION": (
            "Verify account disablement and the termination event.",
            "Enumerate every remaining application, group, and permission.",
            "Revoke residual access while preserving identity and audit history.",
        ),
        "UNAUTHORIZED_GROUP": (
            "Check whether membership is direct or role-derived.",
            "Validate an approved exception or remove the membership.",
            "Review the granting actor and related correlation ID.",
        ),
        "INSECURE_WORKLOAD_CREDENTIAL": (
            "Confirm no credential value is printed or stored in logs.",
            "Identify a managed identity, federated identity, or short-lived role alternative.",
            "Remove and rotate the real credential through the owning platform if this were live.",
        ),
        "MISSING_REQUIRED_ACCESS": (
            "Confirm the user exists, is active, and has the correct role.",
            "Check required group and application assignments.",
            "Restore only the missing role-approved access and retest.",
        ),
    }
    return (*common, *scenario_steps[finding.scenario_type])
