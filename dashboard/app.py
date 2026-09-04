"""CILAMP Phase 1 IAM Command Center."""

from __future__ import annotations

import platform

import streamlit as st

from cilamp import __version__
from cilamp.config import load_settings
from cilamp.database import check_database
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
from cilamp.repository import (
    distribution,
    get_assigned_access,
    get_employee,
    initialize_organization,
    lifecycle_counts,
    list_employees,
    list_audit_events,
    organization_counts,
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
    ("Overview", "Organization Explorer", "JML Operations", "Access Matrix"),
)
st.sidebar.markdown(f"**Mode:** `{settings.mode}`")
st.sidebar.caption("Cloud integrations are disconnected")

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
        "Fictional identities and expected access only; no cloud connections or live writes.</div>",
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
            "Microsoft Entra ID, Azure, and AWS are **not connected**. "
            "All identities and access shown here are fictional simulation data."
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


if page == "Overview":
    render_overview()
elif page == "Organization Explorer":
    render_organization_explorer()
elif page == "JML Operations":
    render_jml_operations()
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

st.caption("CILAMP Phase 2 · Cloud/IAM-first · Simulation-only")
