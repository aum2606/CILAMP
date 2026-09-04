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
    effective_access,
    initialize_organization,
    list_employees,
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
    ("Overview", "Organization Explorer", "Access Matrix"),
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
    access = effective_access(employee)
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
        st.caption("Access source: role-based assignment")

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


if page == "Overview":
    render_overview()
elif page == "Organization Explorer":
    render_organization_explorer()
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

st.caption("CILAMP Phase 1 · Cloud/IAM-first · Simulation-only")
