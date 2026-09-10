"""CILAMP IAM Command Center."""

from __future__ import annotations

import platform

import streamlit as st

from cilamp import __version__
from cilamp.access_review_service import (
    create_developer_admin_scenario,
    remediate_employee,
    review_all,
    review_employee,
    review_summary,
)
from cilamp.config import load_settings
from cilamp.azure_policy import ACTION_LABELS, evaluate_azure_access
from cilamp.azure_repository import (
    get_azure_sync_state,
    initialize_azure_store,
    list_azure_identities,
    list_azure_operations,
    list_azure_resources,
    list_azure_role_assignments,
)
from cilamp.azure_service import AzureSafetyError, synchronize_azure
from cilamp.aws_policy import ACTION_LABELS as AWS_ACTION_LABELS, evaluate_aws_access
from cilamp.aws_repository import (
    get_aws_sync_state,
    initialize_aws_store,
    list_aws_bindings,
    list_aws_cloudtrail_events,
    list_aws_operations,
    list_aws_policies,
    list_aws_resources,
    list_aws_roles,
)
from cilamp.aws_service import AwsSafetyError, synchronize_aws
from cilamp.connectors.aws import AwsConnectorError
from cilamp.connectors.azure import AzureConnectorError
from cilamp.connectors.entra import EntraConnectorError
from cilamp.domain import RiskLevel
from cilamp.database import check_database
from cilamp.entra_repository import (
    get_entra_sync_state,
    initialize_entra_store,
    list_cached_group_member_ids,
    list_entra_directory_audits,
    list_entra_groups,
    list_entra_operations,
    list_entra_service_principals,
    list_entra_users,
)
from cilamp.entra_service import (
    READ_PERMISSIONS,
    WRITE_PERMISSIONS,
    EntraSafetyError,
    change_entra_group_membership,
    refresh_group_members,
    synchronize_entra,
    update_entra_user,
)
from cilamp.iam_catalog import (
    APPLICATIONS,
    DEPARTMENT_NAMES,
    GROUP_NAMES,
    PERMISSIONS,
    ROLE_NAMES,
    access_matrix_rows,
    roles_for_department,
)
from cilamp.lifecycle import LifecycleValidationError
from cilamp.lifecycle_service import (
    execute,
    preview_joiner,
    preview_leaver,
    preview_mover,
)
from cilamp.project_status import (
    CURRENT_PHASE,
    MODULE_STATUSES,
    PROJECT_NAME,
    PROJECT_SHORT_NAME,
    RECENT_MILESTONES,
    completed_module_count,
)
from cilamp.policy import access_source_rows
from cilamp.repository import (
    audit_statistics,
    distribution,
    get_assigned_access,
    get_employee,
    initialize_organization,
    lifecycle_counts,
    list_employees,
    list_audit_events,
    list_security_findings,
    organization_counts,
)
from cilamp.security import SCENARIOS, troubleshooting_steps
from cilamp.security_service import (
    create_security_scenario,
    eligible_employees,
    preview_security_scenario,
    remediate_security_finding,
)


st.set_page_config(
    page_title="CILAMP | IAM Command Center",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 1.7rem; padding-bottom: 3rem;}
    .cilamp-banner {
        padding: 1.35rem 1.55rem; border: 1px solid #23456b; border-radius: 14px;
        background: linear-gradient(120deg, #0c1b2a, #12395a); margin-bottom: 1rem;
    }
    .cilamp-banner h1 {color: #f4f8fb; margin: 0; font-size: 2.05rem;}
    .cilamp-banner p {color: #bcd3e8; margin: .35rem 0 0;}
    .mode-pill {
        display: inline-block; padding: .25rem .7rem; border-radius: 999px;
        background: #0d6b4d; color: white; font-weight: 700; letter-spacing: .04em;
    }
    .context-note {
        border-left: 4px solid #3e8ed0; padding: .65rem 1rem;
        background: rgba(62, 142, 208, .08); border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

settings = load_settings()
try:
    initialize_organization(settings.database_path)
    initialize_entra_store(settings.database_path)
    initialize_azure_store(settings.database_path)
    initialize_aws_store(settings.database_path)
except Exception as error:
    st.error(
        "Organization data could not be initialized. "
        f"Check the configured database path and permissions ({type(error).__name__})."
    )
    st.stop()
database = check_database(settings.database_path)
if not database.healthy:
    st.error(database.message)
    st.stop()
counts = organization_counts(settings.database_path)

st.sidebar.title("CILAMP")
page = st.sidebar.radio(
    "Navigate",
    (
        "Overview",
        "Organization Explorer",
        "JML Operations",
        "Access Review",
        "Security & Audit",
        "Microsoft Entra",
        "Azure Access",
        "AWS Access",
        "Access Matrix",
    ),
)
st.sidebar.markdown(f"**Mode:** `{settings.mode}`")
st.sidebar.caption(
    "Cloud lab connectors are read-only by default"
    if settings.mode == "LIVE_LAB"
    else "Cloud access is simulated"
)

st.markdown(
    f"""
    <div class="cilamp-banner">
      <h1>{PROJECT_SHORT_NAME}</h1>
      <p>{PROJECT_NAME}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

mode_col, phase_col = st.columns([1, 2])
with mode_col:
    st.caption("SYSTEM MODE")
    st.markdown(f'<span class="mode-pill">{settings.mode}</span>', unsafe_allow_html=True)
with phase_col:
    st.caption("CURRENT PHASE")
    st.markdown(
        f'<div class="context-note"><strong>{CURRENT_PHASE}</strong><br>'
        "Azure identity and RBAC are simulation-first; live discovery is explicitly guarded.</div>",
        unsafe_allow_html=True,
    )


def render_overview() -> None:
    st.header("Project Control Center")
    employee_col, department_col, role_col, app_health_col, db_health_col = st.columns(5)
    employee_col.metric("Employees", counts["employees"])
    department_col.metric("Departments", counts["departments"])
    role_col.metric("Job roles", counts["roles"])
    app_health_col.metric("Application", "HEALTHY")
    db_health_col.metric("SQLite", database.status)

    group_col, app_col, completed_col, version_col = st.columns(4)
    group_col.metric("IAM groups", counts["groups"])
    app_col.metric("Applications", counts["applications"])
    completed_col.metric("Completed modules", completed_module_count())
    version_col.metric("Build", f"v{__version__}")

    lifecycle = lifecycle_counts(settings.database_path)
    joiner_col, mover_col, leaver_col = st.columns(3)
    joiner_col.metric("Joiner operations", lifecycle["JOINER"])
    mover_col.metric("Mover operations", lifecycle["MOVER"])
    leaver_col.metric("Leaver operations", lifecycle["LEAVER"])

    access_summary = review_summary(review_all(settings.database_path))
    compliant_col, findings_col, privileged_col, creep_col = st.columns(4)
    compliant_col.metric("Compliant identities", access_summary["compliant"])
    findings_col.metric("Access findings", access_summary["findings"])
    privileged_col.metric("Privileged identities", access_summary["privileged"])
    creep_col.metric("Privilege-creep identities", access_summary["privilege_creep"])

    security_summary = audit_statistics(settings.database_path)
    audit_col, failed_col, open_col, remediated_col = st.columns(4)
    audit_col.metric("Audit events", security_summary["events"])
    failed_col.metric("Failed control checks", security_summary["failed"])
    open_col.metric("Open security findings", security_summary["open_findings"])
    remediated_col.metric(
        "Remediated findings", security_summary["remediated_findings"]
    )

    entra_state = get_entra_sync_state(settings.database_path)
    entra_col, entra_users_col, entra_apps_col = st.columns(3)
    entra_col.metric("Entra connector", entra_state.status)
    entra_users_col.metric("Synced Entra users", entra_state.user_count)
    entra_apps_col.metric(
        "Application identities", entra_state.service_principal_count
    )

    azure_state = get_azure_sync_state(settings.database_path)
    azure_col, resources_col, assignments_col = st.columns(3)
    azure_col.metric("Azure connector", azure_state.status)
    resources_col.metric("Azure resources", azure_state.resource_count)
    assignments_col.metric("Azure RBAC assignments", azure_state.assignment_count)

    chart_col, role_chart_col = st.columns(2)
    with chart_col:
        st.subheader("Department distribution")
        st.bar_chart(
            distribution(settings.database_path, "department"),
            x="department",
            y="Employees",
            horizontal=True,
        )
    with role_chart_col:
        st.subheader("Role distribution")
        st.bar_chart(
            distribution(settings.database_path, "job_role"),
            x="job_role",
            y="Employees",
            horizontal=True,
        )

    st.subheader("IAM capability roadmap")
    st.dataframe(
        [
            {"Module": item.module, "Status": item.status, "IAM purpose": item.purpose}
            for item in MODULE_STATUSES
        ],
        width="stretch",
        hide_index=True,
    )

    milestone_col, cloud_col = st.columns(2)
    with milestone_col:
        st.subheader("Recent milestones")
        for milestone in RECENT_MILESTONES:
            st.markdown(f"✓ {milestone}")
    with cloud_col:
        st.subheader("Cloud integration")
        st.info(
            "Entra and Azure support simulation plus explicitly guarded lab connectors; "
            "AWS is not connected. No live success is shown unless a provider call returns it."
        )


def render_employee_profile(employee) -> None:
    access = get_assigned_access(settings.database_path, employee.employee_id)
    st.subheader("Employee profile")
    identity_col, assignment_col = st.columns(2)
    with identity_col:
        st.markdown(f"**{employee.display_name}**")
        st.write(f"Employee ID: `{employee.employee_id}`")
        st.write(f"Email: `{employee.email}`")
        st.write(f"Status: **{employee.status.value}**")
    with assignment_col:
        st.write(f"Department: **{employee.department}**")
        st.write(f"Job role: **{employee.job_role}**")
        st.caption("Actual access assignments managed by lifecycle operations")

    groups_tab, apps_tab, permissions_tab = st.tabs(
        ("Groups", "Applications", "Permissions")
    )
    with groups_tab:
        st.write(list(access.groups))
    with apps_tab:
        st.write(list(access.applications))
    with permissions_tab:
        st.write(list(access.permissions))


def render_organization_explorer() -> None:
    st.header("Organization Explorer")
    st.caption(
        "Search fictional identities and inspect the access derived from each employee's approved job role."
    )

    search_col, department_col, role_col, status_col = st.columns([2, 1, 1.4, 1])
    with search_col:
        search = st.text_input("Search", placeholder="Name, employee ID, or email")
    with department_col:
        department_choice = st.selectbox("Department", ("All", *DEPARTMENT_NAMES))
    with role_col:
        available_roles = (
            tuple(role.name for role in roles_for_department(department_choice))
            if department_choice != "All"
            else ROLE_NAMES
        )
        role_choice = st.selectbox("Job role", ("All", *available_roles))
    with status_col:
        status_choice = st.selectbox("Status", ("All", "ACTIVE", "DISABLED"))

    employees = list_employees(
        settings.database_path,
        search=search,
        department=None if department_choice == "All" else department_choice,
        job_role=None if role_choice == "All" else role_choice,
        status=None if status_choice == "All" else status_choice,
    )

    st.metric("Matching employees", len(employees))
    st.dataframe(
        [
            {
                "Employee ID": employee.employee_id,
                "Name": employee.display_name,
                "Department": employee.department,
                "Job Role": employee.job_role,
                "Status": employee.status.value,
            }
            for employee in employees
        ],
        width="stretch",
        hide_index=True,
    )

    if employees:
        selected_id = st.selectbox(
            "Open employee profile",
            tuple(employee.employee_id for employee in employees),
            format_func=lambda identifier: next(
                f"{employee.display_name} · {identifier}"
                for employee in employees
                if employee.employee_id == identifier
            ),
        )
        selected_employee = next(
            employee for employee in employees if employee.employee_id == selected_id
        )
        render_employee_profile(selected_employee)
    else:
        st.warning("No fictional employees match the selected filters.")


def render_access_matrix() -> None:
    st.header("Role-Based Access Matrix")
    st.caption(
        "Expected access flows from job role → groups → applications → permissions. "
        "Direct user grants are not part of the Phase 1 model."
    )

    matrix_tab, groups_tab, apps_tab, permissions_tab = st.tabs(
        ("Access Matrix", "Groups", "Applications", "Permissions")
    )
    with matrix_tab:
        st.dataframe(access_matrix_rows(), width="stretch", hide_index=True)
    with groups_tab:
        st.dataframe(
            [{"Group": name} for name in GROUP_NAMES], width="stretch", hide_index=True
        )
    with apps_tab:
        st.dataframe(
            [
                {"Application": item.name, "Sensitivity": item.sensitivity}
                for item in APPLICATIONS
            ],
            width="stretch",
            hide_index=True,
        )
    with permissions_tab:
        st.dataframe(
            [
                {"Permission": item.name, "Purpose": item.description}
                for item in PERMISSIONS
            ],
            width="stretch",
            hide_index=True,
        )

    st.info(
        "Least-privilege example: Developers receive approved development read access, "
        "but not Finance, HR, or cloud-administration permissions."
    )


def _access_columns(access, empty_message: str = "None") -> None:
    groups_col, apps_col, permissions_col = st.columns(3)
    with groups_col:
        st.markdown("**Groups**")
        st.write(list(access.groups) if access.groups else empty_message)
    with apps_col:
        st.markdown("**Applications**")
        st.write(list(access.applications) if access.applications else empty_message)
    with permissions_col:
        st.markdown("**Permissions**")
        st.write(list(access.permissions) if access.permissions else empty_message)


def _render_pending_plan(plan, state_key: str) -> None:
    st.markdown("#### Identity transition")
    before = plan.before_employee
    before_label = (
        "Identity does not exist"
        if before is None
        else f"{before.department} · {before.job_role} · {before.status.value}"
    )
    after = plan.after_employee
    identity_col, arrow_col, result_col = st.columns([4, 1, 4])
    identity_col.info(f"BEFORE\n\n{before_label}")
    arrow_col.markdown("### →")
    result_col.success(
        f"AFTER\n\n{after.department} · {after.job_role} · {after.status.value}"
    )

    st.markdown("#### Access to remove")
    _access_columns(plan.to_remove)
    st.markdown("#### Access to add")
    _access_columns(plan.to_add)

    if plan.operation == "MOVER":
        st.caption(
            "Execution order: revoke obsolete permissions, groups, and applications; "
            "update the identity; then grant the new role's access."
        )
    elif plan.operation == "LEAVER":
        st.warning("This will disable the simulated identity and revoke all assigned access.")

    confirmation_key = (
        f"confirm_{plan.operation}_{plan.employee_id}_{plan.after_employee.job_role}"
    )
    confirmed = st.checkbox(
        f"I confirm this simulated {plan.operation.lower()} operation",
        key=confirmation_key,
    )
    if st.button(
        f"Execute {plan.operation.title()}",
        type="primary",
        disabled=not confirmed,
        key=f"execute_{state_key}",
    ):
        try:
            correlation_id = execute(settings.database_path, plan)
            st.session_state["last_jml_result"] = {
                "operation": plan.operation,
                "employee_id": plan.employee_id,
                "correlation_id": correlation_id,
            }
            del st.session_state[state_key]
            st.rerun()
        except (ValueError, RuntimeError) as error:
            st.error(str(error))


def _render_last_result() -> None:
    result = st.session_state.get("last_jml_result")
    if not result:
        return
    st.success(
        f"{result['operation'].title()} completed for {result['employee_id']} · "
        f"correlation `{result['correlation_id']}`"
    )
    employee = get_employee(settings.database_path, result["employee_id"])
    if employee:
        render_employee_profile(employee)
    events = list_audit_events(
        settings.database_path, target_identity=result["employee_id"], limit=50
    )
    matching_events = [
        event for event in events if event.correlation_id == result["correlation_id"]
    ]
    st.markdown("#### Audit actions")
    st.dataframe(
        [
            {
                "Timestamp": event.timestamp.isoformat(),
                "Action": event.action,
                "Result": event.result,
                "Actor": event.actor,
                "Correlation ID": event.correlation_id,
            }
            for event in matching_events
        ],
        width="stretch",
        hide_index=True,
    )
    if st.button("Dismiss result"):
        del st.session_state["last_jml_result"]
        st.rerun()


def _render_joiner() -> None:
    st.markdown("### Joiner · create identity and grant role access")
    st.caption("Use fictional information only. The department constrains compatible roles.")
    department = st.selectbox("Department", DEPARTMENT_NAMES, key="joiner_department")
    compatible_roles = tuple(role.name for role in roles_for_department(department))
    job_role = st.selectbox("Job role", compatible_roles, key="joiner_role")
    display_name = st.text_input("Fictional employee name", key="joiner_name")
    email = st.text_input(
        "Fictional email", placeholder="new.employee@example.cilamp", key="joiner_email"
    )
    reason = st.text_input(
        "Business reason", value="New employee onboarding", key="joiner_reason"
    )
    if st.button("Preview Joiner", key="preview_joiner"):
        try:
            st.session_state["joiner_plan"] = preview_joiner(
                settings.database_path, display_name, email, job_role, reason
            )
        except LifecycleValidationError as error:
            st.error(str(error))
    plan = st.session_state.get("joiner_plan")
    if plan:
        _render_pending_plan(plan, "joiner_plan")


def _render_mover() -> None:
    st.markdown("### Mover · replace obsolete access")
    active_employees = list_employees(settings.database_path, status="ACTIVE")
    employee_id = st.selectbox(
        "Employee",
        tuple(employee.employee_id for employee in active_employees),
        format_func=lambda identifier: next(
            f"{employee.display_name} · {identifier} · {employee.job_role}"
            for employee in active_employees
            if employee.employee_id == identifier
        ),
        key="mover_employee",
    )
    target_department = st.selectbox(
        "New department", DEPARTMENT_NAMES, key="mover_department"
    )
    target_roles = tuple(role.name for role in roles_for_department(target_department))
    target_role = st.selectbox("New job role", target_roles, key="mover_role")
    reason = st.text_input(
        "Business reason", value="Approved department or role change", key="mover_reason"
    )
    if st.button("Preview Mover", key="preview_mover"):
        try:
            st.session_state["mover_plan"] = preview_mover(
                settings.database_path, employee_id, target_role, reason
            )
        except LifecycleValidationError as error:
            st.error(str(error))
    plan = st.session_state.get("mover_plan")
    if plan:
        _render_pending_plan(plan, "mover_plan")


def _render_leaver() -> None:
    st.markdown("### Leaver · disable identity and revoke all access")
    active_employees = list_employees(settings.database_path, status="ACTIVE")
    employee_id = st.selectbox(
        "Employee",
        tuple(employee.employee_id for employee in active_employees),
        format_func=lambda identifier: next(
            f"{employee.display_name} · {identifier} · {employee.job_role}"
            for employee in active_employees
            if employee.employee_id == identifier
        ),
        key="leaver_employee",
    )
    reason = st.text_input(
        "Termination reason", value="Employment ended", key="leaver_reason"
    )
    if st.button("Preview Leaver", key="preview_leaver"):
        try:
            st.session_state["leaver_plan"] = preview_leaver(
                settings.database_path, employee_id, reason
            )
        except LifecycleValidationError as error:
            st.error(str(error))
    plan = st.session_state.get("leaver_plan")
    if plan:
        _render_pending_plan(plan, "leaver_plan")


def render_jml_operations() -> None:
    st.header("JML Operations Console")
    st.info(
        "SIMULATION MODE: operations modify only the local fictional identity store. "
        "Every confirmed change receives a correlation ID and audit trail."
    )
    _render_last_result()
    joiner_tab, mover_tab, leaver_tab, audit_tab = st.tabs(
        ("Joiner", "Mover", "Leaver", "Audit Timeline")
    )
    with joiner_tab:
        _render_joiner()
    with mover_tab:
        _render_mover()
    with leaver_tab:
        _render_leaver()
    with audit_tab:
        events = list_audit_events(settings.database_path, limit=100)
        st.dataframe(
            [
                {
                    "Timestamp": event.timestamp.isoformat(),
                    "Actor": event.actor,
                    "Identity": event.target_identity,
                    "Action": event.action,
                    "Old State": event.old_state,
                    "New State": event.new_state,
                    "Result": event.result,
                    "Reason": event.reason,
                    "Correlation ID": event.correlation_id,
                }
                for event in events
            ],
            width="stretch",
            hide_index=True,
        )
        if not events:
            st.caption("No lifecycle events have been executed yet.")


def _entitlement_comparison(review) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for label, expected_values, actual_values in (
        ("Group", review.expected.groups, review.actual.groups),
        ("Application", review.expected.applications, review.actual.applications),
        ("Permission", review.expected.permissions, review.actual.permissions),
    ):
        for entitlement in sorted(set(expected_values) | set(actual_values)):
            expected = entitlement in expected_values
            actual = entitlement in actual_values
            rows.append(
                {
                    "Type": label,
                    "Entitlement": entitlement,
                    "Expected": "Yes" if expected else "No",
                    "Actual": "Yes" if actual else "No",
                    "Assessment": (
                        "MATCH"
                        if expected == actual
                        else "EXCESS"
                        if actual
                        else "MISSING"
                    ),
                }
            )
    return rows


def _render_access_review_detail(review) -> None:
    st.subheader(f"Access review · {review.employee.display_name}")
    status_col, role_col, privilege_col = st.columns(3)
    status_col.metric("Identity status", review.employee.status.value)
    role_col.metric("Role", review.employee.job_role)
    privilege_col.metric("Privileged identity", "YES" if review.privileged else "NO")

    expected_tab, actual_tab, difference_tab, source_tab = st.tabs(
        ("Expected Access", "Actual Access", "Differences", "Access Sources")
    )
    with expected_tab:
        _access_columns(review.expected)
    with actual_tab:
        _access_columns(review.actual)
    with difference_tab:
        st.dataframe(
            _entitlement_comparison(review), width="stretch", hide_index=True
        )
    with source_tab:
        st.dataframe(access_source_rows(review), width="stretch", hide_index=True)

    st.markdown("#### Violations and access gaps")
    if review.compliant:
        st.success("COMPLIANT · Actual access matches the approved role baseline.")
        return

    st.dataframe(
        [
            {
                "Risk": finding.risk.value,
                "Category": finding.category,
                "Type": finding.entitlement_type,
                "Entitlement": finding.entitlement,
                "Why flagged": finding.explanation,
                "Suggested remediation": finding.suggested_remediation,
            }
            for finding in review.findings
        ],
        width="stretch",
        hide_index=True,
    )
    st.warning(
        "Remediation will remove unauthorized access and restore missing role-approved "
        "access. The employee's role is not changed."
    )
    confirm_key = f"confirm_remediation_{review.employee.employee_id}"
    confirmed = st.checkbox(
        "I confirm this simulated least-privilege remediation", key=confirm_key
    )
    if st.button(
        "Remediate to Role Baseline",
        type="primary",
        disabled=not confirmed,
        key=f"remediate_{review.employee.employee_id}",
    ):
        try:
            correlation_id = remediate_employee(settings.database_path, review)
            st.session_state["access_review_message"] = (
                f"Access remediated for {review.employee.employee_id} · "
                f"correlation {correlation_id}"
            )
            st.rerun()
        except RuntimeError as error:
            st.error(str(error))


def render_access_review() -> None:
    st.header("RBAC & Access Review Center")
    st.caption(
        "Compare expected role-based access with actual persisted assignments, explain "
        "violations, and remediate safely in simulation mode."
    )
    if message := st.session_state.pop("access_review_message", None):
        st.success(message)

    reviews = review_all(settings.database_path)
    summary = review_summary(reviews)
    identities_col, compliant_col, finding_col, critical_col, privileged_col = st.columns(5)
    identities_col.metric("Reviewed identities", summary["identities"])
    compliant_col.metric("Compliant", summary["compliant"])
    finding_col.metric("Findings", summary["findings"])
    critical_col.metric("Critical", summary["critical"])
    privileged_col.metric("Privileged", summary["privileged"])

    with st.expander("Create mandatory excessive-privilege scenario"):
        st.warning(
            "This controlled simulation grants `platform.administrator` to a Developer so "
            "the policy engine can detect and remediate the violation. No cloud is affected."
        )
        developers = [
            review for review in reviews if review.employee.job_role == "Developer"
        ]
        scenario_employee_id = st.selectbox(
            "Developer",
            tuple(review.employee.employee_id for review in developers),
            format_func=lambda identifier: next(
                f"{review.employee.display_name} · {identifier}"
                for review in developers
                if review.employee.employee_id == identifier
            ),
            key="scenario_developer",
        )
        scenario_confirmed = st.checkbox(
            "I confirm creation of this simulated policy violation",
            key="confirm_admin_scenario",
        )
        if st.button(
            "Grant Simulated Administrator Permission",
            disabled=not scenario_confirmed,
            key="create_admin_scenario",
        ):
            try:
                correlation_id = create_developer_admin_scenario(
                    settings.database_path, scenario_employee_id
                )
                st.session_state["access_review_message"] = (
                    f"Scenario created for {scenario_employee_id} · correlation "
                    f"{correlation_id}"
                )
                st.rerun()
            except (ValueError, RuntimeError) as error:
                st.error(str(error))

    search_col, department_col, category_col, risk_col = st.columns([2, 1, 1.4, 1])
    with search_col:
        search = st.text_input(
            "Search reviews", placeholder="Name or employee ID", key="review_search"
        ).strip().lower()
    with department_col:
        department = st.selectbox(
            "Department", ("All", *DEPARTMENT_NAMES), key="review_department"
        )
    categories = tuple(
        sorted({finding.category for review in reviews for finding in review.findings})
    )
    with category_col:
        category = st.selectbox(
            "Finding category", ("All", "Compliant", *categories), key="review_category"
        )
    with risk_col:
        risk = st.selectbox(
            "Risk", ("All", *(item.value for item in RiskLevel)), key="review_risk"
        )

    filtered = []
    for review in reviews:
        if search and search not in (
            f"{review.employee.display_name} {review.employee.employee_id}".lower()
        ):
            continue
        if department != "All" and review.employee.department != department:
            continue
        if category == "Compliant" and not review.compliant:
            continue
        if category not in {"All", "Compliant"} and not any(
            finding.category == category for finding in review.findings
        ):
            continue
        if risk != "All" and not any(
            finding.risk.value == risk for finding in review.findings
        ):
            continue
        filtered.append(review)

    st.metric("Matching reviews", len(filtered))
    st.dataframe(
        [
            {
                "Employee ID": review.employee.employee_id,
                "Name": review.employee.display_name,
                "Department": review.employee.department,
                "Role": review.employee.job_role,
                "Review": "COMPLIANT" if review.compliant else "VIOLATION",
                "Findings": len(review.findings),
                "Privileged": "Yes" if review.privileged else "No",
                "Privilege Creep": "Yes" if review.privilege_creep else "No",
            }
            for review in filtered
        ],
        width="stretch",
        hide_index=True,
    )

    if filtered:
        selected_id = st.selectbox(
            "Inspect identity",
            tuple(review.employee.employee_id for review in filtered),
            format_func=lambda identifier: next(
                f"{review.employee.display_name} · {identifier} · "
                f"{'COMPLIANT' if review.compliant else 'VIOLATION'}"
                for review in filtered
                if review.employee.employee_id == identifier
            ),
            key="review_identity",
        )
        _render_access_review_detail(
            next(review for review in filtered if review.employee.employee_id == selected_id)
        )
    else:
        st.info("No access reviews match the selected filters.")

    with st.expander("Privileged identity inventory"):
        st.dataframe(
            [
                {
                    "Employee ID": review.employee.employee_id,
                    "Name": review.employee.display_name,
                    "Role": review.employee.job_role,
                    "Status": review.employee.status.value,
                    "Findings": len(review.findings),
                }
                for review in reviews
                if review.privileged
            ],
            width="stretch",
            hide_index=True,
        )


def _audit_category(action: str, result: str) -> str:
    if result == "FAILURE":
        return "Failed operations"
    if action.startswith(("JOINER_", "MOVER_", "LEAVER_")) or action in {
        "IDENTITY_CREATED",
        "IDENTITY_UPDATED",
        "ACCOUNT_DISABLED",
    }:
        return "Lifecycle"
    if any(word in action for word in ("GRANTED", "REVOKED", "REMEDIATION")):
        return "Access changes"
    if any(
        word in action
        for word in ("SECURITY", "SCENARIO", "CHECK", "REVIEW", "VIOLATION")
    ):
        return "Security"
    return "Other"


def _audit_rows(events) -> list[dict[str, str]]:
    return [
        {
            "Timestamp": event.timestamp.isoformat(),
            "Category": _audit_category(event.action, event.result),
            "Result": event.result,
            "Actor": event.actor,
            "Identity": event.target_identity,
            "Action": event.action,
            "Old State": event.old_state,
            "New State": event.new_state,
            "Reason": event.reason,
            "Event ID": event.event_id,
            "Correlation ID": event.correlation_id,
        }
        for event in events
    ]


def _render_security_scenarios() -> None:
    st.subheader("Security Scenario Lab")
    st.warning(
        "Each scenario intentionally creates a local security problem for learning. "
        "No real credential value or cloud resource is used. Preview and confirmation are required."
    )
    scenario_type = st.selectbox(
        "Scenario",
        tuple(scenario.scenario_type for scenario in SCENARIOS),
        format_func=lambda value: next(
            scenario.title for scenario in SCENARIOS if scenario.scenario_type == value
        ),
        key="security_scenario_type",
    )
    definition = next(
        scenario for scenario in SCENARIOS if scenario.scenario_type == scenario_type
    )
    st.caption(definition.purpose)
    candidates = eligible_employees(settings.database_path, scenario_type)
    employee_id = None
    if candidates:
        employee_id = st.selectbox(
            "Scenario target",
            tuple(employee.employee_id for employee in candidates),
            format_func=lambda identifier: next(
                f"{employee.display_name} · {identifier} · {employee.job_role}"
                for employee in candidates
                if employee.employee_id == identifier
            ),
            key="security_scenario_target",
        )
    else:
        st.info("Target: `workload:legacy-reporting-app` (simulated workload identity)")

    if st.button("Preview Security Scenario", key="preview_security_scenario"):
        try:
            st.session_state["security_scenario_plan"] = preview_security_scenario(
                settings.database_path, scenario_type, employee_id
            )
        except ValueError as error:
            st.error(str(error))

    plan = st.session_state.get("security_scenario_plan")
    if plan and plan.scenario_type == scenario_type:
        risk_col, target_col = st.columns(2)
        risk_col.metric("Risk", plan.risk.value)
        target_col.metric("Target", plan.target_identity)
        st.markdown(f"**Expected finding:** {plan.title}")
        st.json(plan.evidence)
        if any(
            (
                plan.to_remove.groups,
                plan.to_remove.applications,
                plan.to_remove.permissions,
            )
        ):
            st.markdown("#### Simulated access to remove")
            _access_columns(plan.to_remove)
        if any((plan.to_add.groups, plan.to_add.applications, plan.to_add.permissions)):
            st.markdown("#### Simulated access to add")
            _access_columns(plan.to_add)
        if plan.new_status:
            st.write(f"Simulated status after creation: **{plan.new_status.value}**")
        confirmed = st.checkbox(
            "I understand this intentionally creates a simulated security finding",
            key=f"confirm_security_scenario_{plan.scenario_type}",
        )
        if st.button(
            "Create Scenario and Finding",
            type="primary",
            disabled=not confirmed,
            key="execute_security_scenario",
        ):
            try:
                finding_id, correlation_id = create_security_scenario(
                    settings.database_path, plan
                )
                st.session_state["security_center_message"] = (
                    f"Security finding {finding_id} created · correlation {correlation_id}"
                )
                del st.session_state["security_scenario_plan"]
                st.rerun()
            except RuntimeError as error:
                st.error(str(error))


def _render_security_findings() -> None:
    st.subheader("Security Findings")
    status_col, risk_col, type_col, target_col = st.columns([1, 1, 1.7, 1.5])
    with status_col:
        status = st.selectbox(
            "Status", ("All", "OPEN", "REMEDIATED"), key="finding_status"
        )
    with risk_col:
        risk = st.selectbox(
            "Risk", ("All", *(item.value for item in RiskLevel)), key="finding_risk"
        )
    with type_col:
        scenario_type = st.selectbox(
            "Scenario type",
            ("All", *(scenario.scenario_type for scenario in SCENARIOS)),
            key="finding_scenario",
        )
    with target_col:
        target_search = st.text_input(
            "Target contains", key="finding_target"
        ).strip().lower()

    findings = list_security_findings(
        settings.database_path,
        status=None if status == "All" else status,
        risk=None if risk == "All" else risk,
        scenario_type=None if scenario_type == "All" else scenario_type,
    )
    if target_search:
        findings = [
            finding
            for finding in findings
            if target_search in finding.target_identity.lower()
        ]
    st.dataframe(
        [
            {
                "Created": finding.created_at.isoformat(),
                "Risk": finding.risk.value,
                "Status": finding.status.value,
                "Target": finding.target_identity,
                "Scenario": finding.title,
                "Recommendation": finding.recommendation,
                "Correlation ID": finding.correlation_id,
            }
            for finding in findings
        ],
        width="stretch",
        hide_index=True,
    )
    if not findings:
        st.caption("No security findings match these filters.")


def _render_audit_events() -> None:
    st.subheader("Unified Audit Events")
    all_events = list_audit_events(settings.database_path, limit=1000)
    category_col, result_col, search_col = st.columns([1.2, 1, 2])
    with category_col:
        category = st.selectbox(
            "Category",
            ("All", "Lifecycle", "Access changes", "Security", "Failed operations"),
            key="audit_category",
        )
    with result_col:
        result = st.selectbox(
            "Result", ("All", "SUCCESS", "FAILURE"), key="audit_result"
        )
    with search_col:
        search = st.text_input(
            "Search actor, identity, action, or correlation",
            key="audit_search",
        ).strip().lower()
    events = []
    for event in all_events:
        event_category = _audit_category(event.action, event.result)
        if category != "All" and event_category != category:
            continue
        if result != "All" and event.result != result:
            continue
        searchable = (
            f"{event.actor} {event.target_identity} {event.action} {event.correlation_id}"
        ).lower()
        if search and search not in searchable:
            continue
        events.append(event)
    st.metric("Matching audit events", len(events))
    st.dataframe(_audit_rows(events), width="stretch", hide_index=True)


def _render_identity_timeline() -> None:
    st.subheader("Identity Timeline")
    all_events = list_audit_events(settings.database_path, limit=1000)
    targets = tuple(sorted({event.target_identity for event in all_events}))
    if not targets:
        st.info("Execute a lifecycle operation or security scenario to create a timeline.")
        return
    target = st.selectbox("Identity or workload", targets, key="timeline_target")
    events = [event for event in reversed(all_events) if event.target_identity == target]
    st.dataframe(_audit_rows(events), width="stretch", hide_index=True)


def _render_privileged_activity() -> None:
    st.subheader("Privileged Activity")
    privileged_targets = {
        review.employee.employee_id
        for review in review_all(settings.database_path)
        if review.privileged
    }
    events = [
        event
        for event in list_audit_events(settings.database_path, limit=1000)
        if event.target_identity in privileged_targets
        or "PRIVILEGED" in event.action
        or "administrator" in event.new_state.lower()
    ]
    st.metric("Privileged identities", len(privileged_targets))
    st.dataframe(_audit_rows(events), width="stretch", hide_index=True)
    if not events:
        st.caption("No privileged activity has been recorded yet.")


def _render_troubleshooting() -> None:
    st.subheader("Troubleshooting Assistant")
    findings = list_security_findings(settings.database_path, status="OPEN")
    if not findings:
        st.success("No open security findings require troubleshooting.")
        return
    finding_id = st.selectbox(
        "Open finding",
        tuple(finding.finding_id for finding in findings),
        format_func=lambda identifier: next(
            f"{finding.risk.value} · {finding.title} · {finding.target_identity}"
            for finding in findings
            if finding.finding_id == identifier
        ),
        key="troubleshooting_finding",
    )
    finding = next(item for item in findings if item.finding_id == finding_id)
    st.markdown(f"**Why it matters:** {finding.description}")
    st.json(finding.evidence)
    st.markdown("#### Investigation checklist")
    for index, step in enumerate(troubleshooting_steps(finding), start=1):
        st.write(f"{index}. {step}")
    st.info(f"Recommended action: {finding.recommendation}")
    confirmed = st.checkbox(
        "I confirm simulated remediation of this finding",
        key=f"confirm_security_remediation_{finding.finding_id}",
    )
    if st.button(
        "Remediate Finding",
        type="primary",
        disabled=not confirmed,
        key="remediate_security_finding",
    ):
        try:
            correlation_id, count = remediate_security_finding(
                settings.database_path, finding.finding_id
            )
            st.session_state["security_center_message"] = (
                f"Remediated {count} finding(s) for {finding.target_identity} · "
                f"correlation {correlation_id}"
            )
            st.rerun()
        except (ValueError, RuntimeError) as error:
            st.error(str(error))


def render_security_audit() -> None:
    st.header("Security & Audit Center")
    st.caption(
        "Investigate lifecycle changes, policy violations, failed control checks, "
        "privileged activity, and simulated security cases."
    )
    if message := st.session_state.pop("security_center_message", None):
        st.success(message)
    statistics = audit_statistics(settings.database_path)
    event_col, failed_col, open_col, closed_col = st.columns(4)
    event_col.metric("Audit events", statistics["events"])
    failed_col.metric("Failed operations", statistics["failed"])
    open_col.metric("Open findings", statistics["open_findings"])
    closed_col.metric("Remediated findings", statistics["remediated_findings"])

    scenario_tab, finding_tab, audit_tab, timeline_tab, privileged_tab, help_tab = st.tabs(
        (
            "Scenario Lab",
            "Security Findings",
            "Audit Events",
            "Identity Timeline",
            "Privileged Activity",
            "Troubleshooting",
        )
    )
    with scenario_tab:
        _render_security_scenarios()
    with finding_tab:
        _render_security_findings()
    with audit_tab:
        _render_audit_events()
    with timeline_tab:
        _render_identity_timeline()
    with privileged_tab:
        _render_privileged_activity()
    with help_tab:
        _render_troubleshooting()


def _entra_user_rows(users) -> list[dict[str, str]]:
    return [
        {
            "Display name": user.display_name,
            "User principal name": user.user_principal_name,
            "Enabled": "YES" if user.account_enabled else "NO",
            "Department": user.department,
            "Job title": user.job_title,
        }
        for user in users
    ]


def render_microsoft_entra() -> None:
    st.header("Microsoft Entra ID Lab")
    st.caption(
        "A provider-isolated connector. Simulation is local; LIVE_LAB uses Microsoft "
        "Graph only after explicit tenant and write safeguards are configured."
    )
    if message := st.session_state.pop("entra_message", None):
        st.success(message)

    state = get_entra_sync_state(settings.database_path)
    status_col, mode_status_col, tenant_col, sync_col = st.columns(4)
    status_col.metric("Connection", state.status)
    mode_status_col.metric("Mode", settings.mode)
    tenant_col.metric("Tenant", settings.entra_tenant_label)
    sync_col.metric(
        "Last synchronization",
        state.last_synced_at.strftime("%Y-%m-%d %H:%M UTC")
        if state.last_synced_at
        else "Never",
    )
    if settings.mode == "LIVE_LAB":
        if settings.entra_lab_enabled:
            st.warning(
                "LIVE LAB MODE: reads target the configured Entra tenant. Writes are "
                f"{'enabled for allowlisted targets' if settings.entra_writes_enabled else 'disabled'}."
            )
        else:
            st.warning(
                "The global mode is LIVE_LAB, but the Entra connector is disabled in "
                "this Azure-only configuration."
            )
    else:
        st.info("SIMULATION MODE: no Microsoft Graph request or cloud modification occurs.")

    if st.button("Synchronize Entra Directory", type="primary", key="entra_sync"):
        try:
            correlation_id = synchronize_entra(settings)
            st.session_state["entra_message"] = (
                f"Directory synchronization completed · correlation {correlation_id}"
            )
            st.rerun()
        except EntraConnectorError as error:
            st.error(str(error))

    users = list_entra_users(settings.database_path)
    groups = list_entra_groups(settings.database_path)
    principals = list_entra_service_principals(settings.database_path)
    audits = list_entra_directory_audits(settings.database_path)
    operations = list_entra_operations(settings.database_path)
    users_tab, groups_tab, apps_tab, audits_tab, operations_tab, readiness_tab = st.tabs(
        (
            "Synced Users",
            "Groups & Memberships",
            "Application Identities",
            "Directory Audit",
            "Entra Operations",
            "Lab Readiness & Writes",
        )
    )
    with users_tab:
        st.metric("Cached users", len(users))
        st.dataframe(_entra_user_rows(users), width="stretch", hide_index=True)
        if not users:
            st.caption("Synchronize the directory to populate the local display cache.")

    with groups_tab:
        st.metric("Cached groups", len(groups))
        st.dataframe(
            [
                {
                    "Display name": group.display_name,
                    "Type": group.group_type,
                    "Security enabled": "YES" if group.security_enabled else "NO",
                    "Description": group.description,
                }
                for group in groups
            ],
            width="stretch",
            hide_index=True,
        )
        if groups:
            selected_group_id = st.selectbox(
                "Inspect group membership",
                tuple(group.object_id for group in groups),
                format_func=lambda identifier: next(
                    group.display_name for group in groups if group.object_id == identifier
                ),
                key="entra_membership_group",
            )
            if st.button("Refresh Selected Membership", key="entra_refresh_members"):
                try:
                    correlation_id = refresh_group_members(settings, selected_group_id)
                    st.session_state["entra_message"] = (
                        f"Group membership refreshed · correlation {correlation_id}"
                    )
                    st.rerun()
                except (EntraConnectorError, EntraSafetyError) as error:
                    st.error(str(error))
            member_ids = set(
                list_cached_group_member_ids(settings.database_path, selected_group_id)
            )
            st.dataframe(
                _entra_user_rows([user for user in users if user.object_id in member_ids]),
                width="stretch",
                hide_index=True,
            )

    with apps_tab:
        st.metric("Service principals", len(principals))
        st.dataframe(
            [
                {
                    "Display name": item.display_name,
                    "Principal type": item.principal_type,
                    "Enabled": "YES" if item.account_enabled else "NO",
                    "Application ID": (
                        f"{item.application_id[:8]}…{item.application_id[-4:]}"
                        if len(item.application_id) > 14
                        else item.application_id
                    ),
                }
                for item in principals
            ],
            width="stretch",
            hide_index=True,
        )
        st.caption(
            "A service principal is a tenant-local workload identity. It is not a human "
            "user, and no credential value is cached here."
        )

    with audits_tab:
        st.dataframe(
            [
                {
                    "Time": item.activity_at.isoformat(),
                    "Activity": item.activity,
                    "Result": item.result,
                    "Initiated by": item.initiated_by,
                    "Target": item.target,
                }
                for item in audits
            ],
            width="stretch",
            hide_index=True,
        )
        if not audits:
            st.caption(
                "No audit records are cached. AuditLog.Read.All, a supported role, and "
                "applicable tenant retention/licensing may be required."
            )

    with operations_tab:
        st.dataframe(
            [
                {
                    "Time": item.timestamp.isoformat(),
                    "Mode": item.mode,
                    "Action": item.action,
                    "Target": item.target,
                    "Result": item.result,
                    "Details": item.details,
                    "Correlation ID": item.correlation_id,
                }
                for item in operations
            ],
            width="stretch",
            hide_index=True,
        )

    with readiness_tab:
        st.subheader("Least-privilege readiness")
        read_col, write_col = st.columns(2)
        with read_col:
            st.markdown("**Read permissions**")
            for permission in READ_PERMISSIONS:
                st.write(f"- {permission}")
        with write_col:
            st.markdown("**Write permissions (only if enabled)**")
            for permission in WRITE_PERMISSIONS:
                st.write(f"- {permission}")
        for limitation in state.limitations:
            st.warning(limitation)
        st.caption(
            "Conditional Access, PIM, MFA registration, and Lifecycle Workflows are not "
            "claimed as live unless the tenant license and permissions expose them."
        )
        _render_entra_writes(users, groups)


def _render_entra_writes(users, groups) -> None:
    if not users:
        st.info("Synchronize first to preview a selected-user operation.")
        return
    st.markdown("#### Update selected lab user")
    user_id = st.selectbox(
        "User",
        tuple(user.object_id for user in users),
        format_func=lambda identifier: next(
            f"{user.display_name} · {user.user_principal_name}"
            for user in users
            if user.object_id == identifier
        ),
        key="entra_update_user",
    )
    user = next(item for item in users if item.object_id == user_id)
    department = st.text_input(
        "Department", value=user.department, key="entra_update_department"
    )
    job_title = st.text_input(
        "Job title", value=user.job_title, key="entra_update_job_title"
    )
    confirmed = st.checkbox(
        f"I confirm this {settings.mode} selected-user profile update",
        key="entra_confirm_user_update",
    )
    if st.button("Apply User Update", disabled=not confirmed, key="entra_apply_user_update"):
        try:
            correlation_id = update_entra_user(
                settings, user_id, department, job_title, confirmed=confirmed
            )
            st.session_state["entra_message"] = (
                f"User update completed · correlation {correlation_id}"
            )
            st.rerun()
        except (EntraConnectorError, EntraSafetyError) as error:
            st.error(str(error))

    if groups:
        st.markdown("#### Change selected group membership")
        group_id = st.selectbox(
            "Group",
            tuple(group.object_id for group in groups),
            format_func=lambda identifier: next(
                group.display_name for group in groups if group.object_id == identifier
            ),
            key="entra_write_group",
        )
        operation = st.radio("Membership action", ("ADD", "REMOVE"), horizontal=True)
        membership_confirmed = st.checkbox(
            f"I confirm this {settings.mode} membership change",
            key="entra_confirm_membership",
        )
        if st.button(
            "Apply Membership Change",
            disabled=not membership_confirmed,
            key="entra_apply_membership",
        ):
            try:
                correlation_id = change_entra_group_membership(
                    settings,
                    group_id,
                    user_id,
                    operation,
                    confirmed=membership_confirmed,
                )
                st.session_state["entra_message"] = (
                    f"Membership change completed · correlation {correlation_id}"
                )
                st.rerun()
            except (EntraConnectorError, EntraSafetyError) as error:
                st.error(str(error))


def render_azure_access() -> None:
    st.header("Azure Identity & RBAC")
    st.caption(
        "Inspect who can do what, on which Azure scope. LIVE_LAB discovery is "
        "read-only; simulation demonstrates least privilege without cloud changes."
    )
    if message := st.session_state.pop("azure_message", None):
        st.success(message)
    state = get_azure_sync_state(settings.database_path)
    status_col, mode_col, subscription_col, sync_col = st.columns(4)
    status_col.metric("Azure connection", state.status)
    mode_col.metric("Mode", settings.mode)
    subscription_col.metric("Subscription", settings.azure_subscription_label)
    sync_col.metric(
        "Last synchronization",
        state.last_synced_at.strftime("%Y-%m-%d %H:%M UTC")
        if state.last_synced_at
        else "Never",
    )
    st.write(f"Resource-group boundary: **{settings.azure_resource_group}**")
    if settings.mode == "LIVE_LAB":
        st.warning(
            "LIVE LAB MODE: Azure Resource Manager discovery is read-only and limited "
            "to the configured resource group. This page cannot create role assignments."
        )
    else:
        st.info("SIMULATION MODE: no Azure token request or resource operation occurs.")
    if st.button("Synchronize Azure RBAC", type="primary", key="azure_sync"):
        try:
            correlation_id = synchronize_azure(settings)
            st.session_state["azure_message"] = (
                f"Azure RBAC synchronization completed · correlation {correlation_id}"
            )
            st.rerun()
        except (AzureConnectorError, AzureSafetyError) as error:
            st.error(str(error))

    resources = list_azure_resources(settings.database_path)
    identities = list_azure_identities(settings.database_path)
    assignments = list_azure_role_assignments(settings.database_path)
    operations = list_azure_operations(settings.database_path)
    (
        resources_tab,
        identities_tab,
        assignments_tab,
        access_tab,
        managed_tab,
        patterns_tab,
        operations_tab,
    ) = st.tabs(
        (
            "Resources",
            "Identities",
            "RBAC Assignments",
            "Effective Access",
            "Managed Identities",
            "Credential Patterns",
            "Azure Operations",
        )
    )
    with resources_tab:
        st.metric("Resources in scope", len(resources))
        st.dataframe(
            [
                {
                    "Name": item.name,
                    "Type": item.resource_type,
                    "Resource group": item.resource_group,
                    "Location": item.location,
                    "Scope / resource ID": item.resource_id,
                }
                for item in resources
            ],
            width="stretch",
            hide_index=True,
        )
        if not resources:
            st.caption("Synchronize Azure RBAC to populate the display cache.")

    with identities_tab:
        st.metric("Security principals", len(identities))
        st.dataframe(
            [
                {
                    "Identity": item.display_name,
                    "Type": item.identity_type,
                    "Source": item.source_resource,
                    "Credential posture": item.credential_mode,
                }
                for item in identities
            ],
            width="stretch",
            hide_index=True,
        )

    with assignments_tab:
        st.metric("Role assignments", len(assignments))
        st.dataframe(
            [
                {
                    "Principal": item.principal_name,
                    "Principal type": item.principal_type,
                    "Role": item.role_name,
                    "Scope": item.scope,
                }
                for item in assignments
            ],
            width="stretch",
            hide_index=True,
        )
        st.caption(
            "Azure RBAC = security principal + role definition + scope. Child resources "
            "inherit grants from applicable parent scopes."
        )

    with access_tab:
        st.subheader("Allowed and not-granted access")
        st.caption(
            "NOT GRANTED means no cached role assignment grants the action. It is not a "
            "claim that Azure has an explicit deny assignment."
        )
        if resources and identities:
            principal_id = st.selectbox(
                "Security principal",
                tuple(item.principal_id for item in identities),
                format_func=lambda identifier: next(
                    f"{item.display_name} · {item.identity_type}"
                    for item in identities
                    if item.principal_id == identifier
                ),
                key="azure_access_principal",
            )
            resource_id = st.selectbox(
                "Azure resource",
                tuple(item.resource_id for item in resources),
                format_func=lambda identifier: next(
                    f"{item.name} · {item.resource_type}"
                    for item in resources
                    if item.resource_id == identifier
                ),
                key="azure_access_resource",
            )
            action = st.selectbox(
                "Requested action",
                tuple(ACTION_LABELS),
                format_func=lambda value: ACTION_LABELS[value],
                key="azure_access_action",
            )
            identity = next(item for item in identities if item.principal_id == principal_id)
            resource = next(item for item in resources if item.resource_id == resource_id)
            decision = evaluate_azure_access(
                identity.principal_id,
                identity.display_name,
                resource,
                action,
                assignments,
            )
            if decision.decision == "ALLOWED":
                st.success(f"ALLOWED — {decision.rationale}")
            elif decision.decision == "UNKNOWN":
                st.warning(f"UNKNOWN — {decision.rationale}")
            else:
                st.error(f"NOT GRANTED — {decision.rationale}")
            st.write(
                {
                    "Identity": decision.principal_name,
                    "Resource": decision.resource_name,
                    "Action": ACTION_LABELS[decision.action],
                    "Matched granting roles": list(decision.matched_roles),
                }
            )
        else:
            st.info("Synchronize first to evaluate effective access.")

    with managed_tab:
        managed = [
            item for item in identities if "ManagedIdentity" in item.identity_type
        ]
        st.metric("Managed identities", len(managed))
        st.dataframe(
            [
                {
                    "Managed identity": item.display_name,
                    "Type": item.identity_type,
                    "Attached/source resource": item.source_resource,
                    "Credential posture": item.credential_mode,
                    "Assigned roles": ", ".join(
                        sorted(
                            assignment.role_name
                            for assignment in assignments
                            if assignment.principal_id == item.principal_id
                        )
                    ),
                }
                for item in managed
            ],
            width="stretch",
            hide_index=True,
        )
        st.info(
            "A managed identity obtains Entra tokens for its Azure workload. Developers "
            "do not receive or rotate an application password, but RBAC is still required."
        )

    with patterns_tab:
        bad_col, good_col = st.columns(2)
        with bad_col:
            st.error("BAD PATTERN — simulated metadata only")
            st.code("Application\n  ↓\nHardcoded secret\n  ↓\nAzure resource")
            st.write(
                "Secret leakage, manual rotation, and unclear ownership create avoidable risk. "
                "CILAMP stores no example secret value."
            )
        with good_col:
            st.success("PREFERRED PATTERN")
            st.code(
                "Application\n  ↓\nManaged identity\n  ↓\nAzure RBAC at narrow scope\n  ↓\nAzure resource"
            )
            st.write(
                "The platform supplies the workload identity; the role and scope provide "
                "only the resource actions the application needs."
            )

    with operations_tab:
        for limitation in state.limitations:
            st.warning(limitation)
        st.dataframe(
            [
                {
                    "Time": item.timestamp.isoformat(),
                    "Mode": item.mode,
                    "Action": item.action,
                    "Target": item.target,
                    "Result": item.result,
                    "Details": item.details,
                    "Correlation ID": item.correlation_id,
                }
                for item in operations
            ],
            width="stretch",
            hide_index=True,
        )


def render_aws_access() -> None:
    st.header("AWS IAM Access")
    st.caption("Inspect roles, policies, S3 resource access, STS identity patterns, and CloudTrail evidence. Synchronization never changes AWS.")
    if message := st.session_state.pop("aws_message", None):
        st.success(message)
    state = get_aws_sync_state(settings.database_path)
    cols = st.columns(4)
    cols[0].metric("AWS connection", state.status)
    cols[1].metric("Mode", settings.mode)
    cols[2].metric("Account", settings.aws_account_label)
    cols[3].metric("Last synchronization", state.last_synced_at.strftime("%Y-%m-%d %H:%M UTC") if state.last_synced_at else "Never")
    st.write(f"Region: **{settings.aws_region}** · IAM role path boundary: **{settings.aws_role_path}**")
    if settings.mode == "LIVE_LAB":
        st.warning("LIVE LAB MODE: discovery uses STS plus read/list IAM, S3, and CloudTrail APIs. Root identities are rejected; no AWS write API is exposed.")
    else:
        st.info("SIMULATION MODE: no AWS SDK session or cloud request occurs.")
    if st.button("Synchronize AWS IAM", type="primary", key="aws_sync"):
        try:
            correlation_id = synchronize_aws(settings)
            st.session_state["aws_message"] = f"AWS IAM synchronization completed · correlation {correlation_id}"
            st.rerun()
        except (AwsConnectorError, AwsSafetyError) as error:
            st.error(str(error))

    resources = list_aws_resources(settings.database_path)
    roles = list_aws_roles(settings.database_path)
    policies = list_aws_policies(settings.database_path)
    bindings = list_aws_bindings(settings.database_path)
    events = list_aws_cloudtrail_events(settings.database_path)
    operations = list_aws_operations(settings.database_path)
    resources_tab, roles_tab, policies_tab, access_tab, sts_tab, audit_tab, patterns_tab, operations_tab = st.tabs(("Resources", "Roles", "Policies", "Effective Access", "STS Identity", "CloudTrail", "Credential Patterns", "AWS Operations"))
    with resources_tab:
        st.metric("Resources in scope", len(resources))
        st.dataframe([{"Name": x.name, "Type": x.resource_type, "Region": x.region, "ARN": x.arn} for x in resources], width="stretch", hide_index=True)
    with roles_tab:
        st.metric("IAM roles", len(roles))
        st.dataframe([{"Role": x.name, "Path": x.path, "Trusted principal": ", ".join(x.trusted_principals), "Credential posture": x.credential_mode, "ARN": x.arn} for x in roles], width="stretch", hide_index=True)
        st.caption("Roles obtain short-lived STS sessions. CILAMP neither asks for nor stores AWS access keys.")
    with policies_tab:
        rows = [{"Policy": p.name, "Source": p.source, "Effect": s.effect, "Actions": ", ".join(s.actions), "Resources": ", ".join(s.resources), "Conditional": s.has_conditions} for p in policies for s in p.statements]
        st.metric("Policies", len(policies))
        st.dataframe(rows, width="stretch", hide_index=True)
    with access_tab:
        st.subheader("Allowed, explicit-deny, and not-granted access")
        st.caption("This cached identity-policy explanation is educational, not AWS authorization proof. External policy layers and request context can change a live result.")
        if roles and resources:
            role_arn = st.selectbox("IAM role", tuple(x.arn for x in roles), format_func=lambda arn: next(x.name for x in roles if x.arn == arn), key="aws_role")
            resource_arn = st.selectbox("AWS resource", tuple(x.arn for x in resources), format_func=lambda arn: next(x.name for x in resources if x.arn == arn), key="aws_resource")
            action = st.selectbox("Requested action", tuple(AWS_ACTION_LABELS), format_func=lambda value: AWS_ACTION_LABELS[value], key="aws_action")
            role = next(x for x in roles if x.arn == role_arn)
            resource = next(x for x in resources if x.arn == resource_arn)
            decision = evaluate_aws_access(role, resource, action, policies, bindings)
            if decision.decision == "ALLOWED":
                st.success(f"ALLOWED — {decision.rationale}")
            elif decision.decision == "UNKNOWN":
                st.warning(f"UNKNOWN — {decision.rationale}")
            else:
                st.error(f"{decision.decision} — {decision.rationale}")
            st.write({"Role": decision.role_name, "Resource": decision.resource_name, "Action": AWS_ACTION_LABELS[decision.action], "Matched policies": list(decision.matched_policies)})
        else:
            st.info("Synchronize first to evaluate cached access.")
    with sts_tab:
        st.metric("Assumable roles", len(roles))
        st.code("Human or workload\n  ↓ AssumeRole / federation\nAWS STS temporary session\n  ↓\nNarrow IAM policy → AWS resource")
        st.write("Caller identity (display-safe ARN):", state.caller_arn or "Not synchronized")
    with audit_tab:
        st.metric("CloudTrail events", len(events))
        st.dataframe([{"Time": x.event_time.isoformat(), "Event": x.event_name, "Identity": x.username, "Resource": x.resource_name, "Event ID": x.event_id} for x in events], width="stretch", hide_index=True)
        st.caption("Only event metadata is cached. Raw CloudTrail event payloads are not stored or displayed.")
    with patterns_tab:
        bad, good = st.columns(2)
        with bad:
            st.error("BAD PATTERN — metadata only")
            st.code("Application\n  ↓\nHardcoded long-lived access key\n  ↓\nAWS resource")
        with good:
            st.success("PREFERRED PATTERN")
            st.code("Application or user federation\n  ↓\nIAM role + STS temporary session\n  ↓\nLeast-privilege policy\n  ↓\nAWS resource")
    with operations_tab:
        for limitation in state.limitations:
            st.warning(limitation)
        st.dataframe([{"Time": x.timestamp.isoformat(), "Mode": x.mode, "Action": x.action, "Target": x.target, "Result": x.result, "Details": x.details, "Correlation ID": x.correlation_id} for x in operations], width="stretch", hide_index=True)


if page == "Overview":
    render_overview()
elif page == "Organization Explorer":
    render_organization_explorer()
elif page == "JML Operations":
    render_jml_operations()
elif page == "Access Review":
    render_access_review()
elif page == "Security & Audit":
    render_security_audit()
elif page == "Microsoft Entra":
    render_microsoft_entra()
elif page == "Azure Access":
    render_azure_access()
elif page == "AWS Access":
    render_aws_access()
else:
    render_access_matrix()

with st.expander("Runtime details"):
    st.write(
        {
            "Python": platform.python_version(),
            "Database engine": "SQLite",
            "Schema version": database.schema_version,
            "Mode": settings.mode,
        }
    )

st.caption("CILAMP Phase 7 · Cloud/IAM-first · AWS IAM and least privilege")
