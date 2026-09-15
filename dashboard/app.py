"""IAM ConCen — AWS & Identity Lifecycle Platform."""

from __future__ import annotations

import platform
import streamlit as st

from cilamp import __version__
from cilamp.access_review_service import (
    create_developer_admin_scenario,
    remediate_employee,
    review_all,
    review_summary,
)
from cilamp.config import load_settings
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
    page_title="IAM ConCen | AWS Identity & Access Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",# Custom Theme-Aware CSS Design System
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* ────────────────────────────────────────────────
       DESIGN TOKENS — Dark mode defaults
    ──────────────────────────────────────────────── */
    :root {
        --text-primary:   #F1F5F9;
        --text-secondary: #94A3B8;
        --text-muted:     #64748B;
        --bg-card:        #1E293B;
        --bg-header:      linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        --border-color:   #334155;
        --accent-blue:    #38BDF8;
        --sidebar-bg:     #0F172A;
        --sidebar-border: #1E293B;
        --sidebar-text:   #F8FAFC;
        --h2-color:       #F1F5F9;
        --h3-color:       #E2E8F0;
    }

    /* ────────────────────────────────────────────────
       LIGHT MODE overrides — Streamlit sets
       [data-theme="light"] on <div stApp>
    ──────────────────────────────────────────────── */
    [data-theme="light"],
    .stApp[data-theme="light"] {
        --text-primary:   #0F172A;
        --text-secondary: #475569;
        --text-muted:     #64748B;
        --bg-card:        #F1F5F9;
        --bg-header:      linear-gradient(135deg, #E2E8F0 0%, #F1F5F9 100%);
        --border-color:   #CBD5E1;
        --accent-blue:    #0369A1;
        --sidebar-bg:     #F8FAFC;
        --sidebar-border: #CBD5E1;
        --sidebar-text:   #0F172A;
        --h2-color:       #1E293B;
        --h3-color:       #334155;
    }

    /* Fallback for system-level light preference when Streamlit theme not yet set */
    @media (prefers-color-scheme: light) {
        :root {
            --text-primary:   #0F172A;
            --text-secondary: #475569;
            --text-muted:     #64748B;
            --bg-card:        #F1F5F9;
            --bg-header:      linear-gradient(135deg, #E2E8F0 0%, #F1F5F9 100%);
            --border-color:   #CBD5E1;
            --accent-blue:    #0369A1;
            --sidebar-bg:     #F8FAFC;
            --sidebar-border: #CBD5E1;
            --sidebar-text:   #0F172A;
            --h2-color:       #1E293B;
            --h3-color:       #334155;
        }
    }

    /* ────────────────────────────────────────────────
       BASE
    ──────────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }

    /* ────────────────────────────────────────────────
       TOP BRAND HEADER
    ──────────────────────────────────────────────── */
    .brand-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: var(--bg-header);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.25rem 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.12);
    }
    .brand-header h1 {
        font-size: 1.6rem !important;
        font-weight: 700;
        color: var(--text-primary) !important;
        margin: 0 !important;
        padding: 0 !important;
        letter-spacing: -0.02em;
    }
    .brand-header p {
        font-size: 0.88rem;
        color: var(--text-secondary);
        margin: 0.2rem 0 0 0;
    }

    /* ────────────────────────────────────────────────
       BADGES
    ──────────────────────────────────────────────── */
    .badge-aws {
        background: rgba(245, 158, 11, 0.15);
        color: #B45309;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 0.3rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    [data-theme="light"] .badge-aws,
    .stApp[data-theme="light"] .badge-aws {
        background: rgba(245, 158, 11, 0.12);
        color: #92400E;
    }
    .badge-mode {
        background: rgba(16, 185, 129, 0.15);
        color: #059669;
        border: 1px solid rgba(16, 185, 129, 0.35);
        padding: 0.3rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    /* Dark mode badge colors */
    [data-theme="dark"] .badge-aws,
    .stApp[data-theme="dark"] .badge-aws { color: #FBBF24; }
    [data-theme="dark"] .badge-mode,
    .stApp[data-theme="dark"] .badge-mode { color: #34D399; }

    /* ────────────────────────────────────────────────
       SECTION TITLES
    ──────────────────────────────────────────────── */
    .section-title {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin: 1rem 0 0.25rem 0 !important;
        letter-spacing: -0.01em;
    }
    .section-subtitle {
        font-size: 0.85rem;
        color: var(--text-secondary);
        margin-bottom: 1.25rem;
    }

    /* ────────────────────────────────────────────────
       SIDEBAR
    ──────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--sidebar-border);
    }
    /* Sidebar radio labels and captions */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] .stCaption {
        color: var(--sidebar-text) !important;
    }
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--sidebar-text) !important;
    }
    .sidebar-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: var(--sidebar-text);
        margin-bottom: 0.4rem;
    }

    /* ────────────────────────────────────────────────
       HEADINGS (h1/h2/h3 inside main content)
    ──────────────────────────────────────────────── */
    h1, h2, h3 {
        font-weight: 600 !important;
    }
    h2 {
        font-size: 1.35rem !important;
        color: var(--h2-color) !important;
        margin-top: 1.25rem !important;
        margin-bottom: 0.75rem !important;
    }
    h3 {
        font-size: 1.1rem !important;
        color: var(--h3-color) !important;
    }

    /* ────────────────────────────────────────────────
       METRICS
    ──────────────────────────────────────────────── */
    [data-testid="stMetricValue"] {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: var(--accent-blue) !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.78rem !important;
        font-weight: 500 !important;
        color: var(--text-secondary) !important;
        white-space: nowrap !important;
    }

    /* ────────────────────────────────────────────────
       BUTTONS
    ──────────────────────────────────────────────── */
    .stButton>button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.45rem 1.2rem !important;
        transition: all 0.2s ease !important;
    }

    /* ────────────────────────────────────────────────
       TABS — make labels visible in both themes
    ──────────────────────────────────────────────── */
    [data-testid="stTab"] button p,
    .stTabs [data-baseweb="tab"] {
        color: var(--text-secondary) !important;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] p,
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: var(--accent-blue) !important;
        font-weight: 600;
    }

    /* ────────────────────────────────────────────────
       DATAFRAMES / TABLES
    ──────────────────────────────────────────────── */
    [data-testid="stDataFrame"] th {
        color: var(--text-primary) !important;
        background: var(--bg-card) !important;
        border-bottom: 1px solid var(--border-color) !important;
        font-weight: 600;
    }
    [data-testid="stDataFrame"] td {
        color: var(--text-primary) !important;
    }

    /* ────────────────────────────────────────────────
       SELECT / INPUT FIELDS
    ──────────────────────────────────────────────── */
    .stSelectbox label, .stTextInput label, .stRadio label {
        color: var(--text-primary) !important;
    }

    /* ────────────────────────────────────────────────
       EXPANDERS
    ──────────────────────────────────────────────── */
    details summary span {
        color: var(--text-primary) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)e,
)

settings = load_settings()
try:
    initialize_organization(settings.database_path)
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

# Sidebar Menu (Clean & Simple)
st.sidebar.markdown('<div class="sidebar-title">IAM ConCen</div>', unsafe_allow_html=True)
st.sidebar.markdown(f'<span class="badge-mode">{settings.mode}</span>', unsafe_allow_html=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    (
        "📊 Dashboard",
        "👥 Employees & Roles",
        "🔄 Join / Move / Leave",
        "🔍 Access Review",
        "🛡️ Security & Audit",
        "☁️ AWS Access",
        "📋 Access Matrix",
    ),
    index=0,
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
# AWS Connection Status
aws_state = get_aws_sync_state(settings.database_path)
aws_connected = aws_state.status == "CONNECTED"
conn_indicator = "🟢" if aws_connected else "🔴"
st.sidebar.caption("**AWS Connection**")
st.sidebar.caption(f"{conn_indicator} {'Connected' if aws_connected else aws_state.status.title()}")
st.sidebar.caption(f"**Region:** `{settings.aws_region}`")
env_label = "Live Lab" if settings.mode == "LIVE_LAB" else "Simulation"
st.sidebar.caption(f"**Environment:** {env_label}")




def render_overview() -> None:
    # Brand header — Dashboard only
    st.markdown(
        f"""
    <div class="brand-header">
        <div>
            <h1>{PROJECT_SHORT_NAME} — AWS IAM Control Centre</h1>
            <p>AWS Identity Lifecycle, Access Reviews, Least Privilege &amp; Security Audit</p>
        </div>
        <div>
            <span class="badge-aws">☁️ AWS INTEGRATED</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Dynamic status checks
    db_health = check_database(settings.database_path)
    db_status = "HEALTHY" if db_health.healthy else "UNHEALTHY"
    aws_state = get_aws_sync_state(settings.database_path)
    aws_status = aws_state.status
    system_healthy = db_health.healthy and counts.get("employees", 0) > 0
    system_status = "HEALTHY" if system_healthy else "UNHEALTHY"

    # Organization Identity Metrics
    m1, m2, m3, m4, m5, m6, m7 = st.columns(7)
    m1.metric("Total Employees", counts["employees"])
    m2.metric("Active", counts.get("active", ""))
    m3.metric("Disabled", counts.get("disabled", ""))
    m4.metric("Departments", counts["departments"])
    m5.metric("Job Roles", counts["roles"])
    m6.metric("IAM Groups", counts["groups"])
    m7.metric("Applications", counts["applications"])

    st.markdown("---")
    st.markdown("### 🔌 Health & Connectivity")
    h1, h2, h3, h4 = st.columns(4)
    h1.metric("System Health", system_status)
    h2.metric("Database", db_status)
    h3.metric("AWS Connection", aws_status)
    h4.metric("Completed Modules", completed_module_count())

    st.markdown("---")
    st.markdown("### ☁️ AWS & Security Health")
    aws_state = get_aws_sync_state(settings.database_path)
    access_summary = review_summary(review_all(settings.database_path))
    security_summary = audit_statistics(settings.database_path)

    aws_col, compliant_col, findings_col, audit_col = st.columns(4)
    aws_col.metric("AWS Status", aws_state.status)
    compliant_col.metric("Compliant Identities", access_summary["compliant"])
    findings_col.metric("Open Findings", security_summary["open_findings"])
    audit_col.metric("Audit Events", security_summary["events"])

    st.markdown("---")
    chart_col, role_chart_col = st.columns(2)
    with chart_col:
        st.markdown("### Department Distribution")
        st.bar_chart(
            distribution(settings.database_path, "department"),
            x="department",
            y="Employees",
            horizontal=True,
        )
    with role_chart_col:
        st.markdown("### Role Distribution")
        st.bar_chart(
            distribution(settings.database_path, "job_role"),
            x="job_role",
            y="Employees",
            horizontal=True,
        )




def render_employee_profile(employee) -> None:
    access = get_assigned_access(settings.database_path, employee.employee_id)
    st.markdown(f"### Employee Profile — {employee.display_name}")
    identity_col, assignment_col = st.columns(2)
    with identity_col:
        st.write(f"**Employee ID:** `{employee.employee_id}`")
        st.write(f"**Email:** `{employee.email}`")
        st.write(f"**Status:** `{employee.status.value}`")
    with assignment_col:
        st.write(f"**Department:** `{employee.department}`")
        st.write(f"**Job Role:** `{employee.job_role}`")

    groups_tab, apps_tab, permissions_tab = st.tabs(
        ("Assigned Groups", "Assigned Applications", "Effective Permissions")
    )
    with groups_tab:
        st.write(list(access.groups))
    with apps_tab:
        st.write(list(access.applications))
    with permissions_tab:
        st.write(list(access.permissions))


def render_organization_explorer() -> None:
    st.markdown('<div class="section-title">Organization Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Search employee identities and inspect their approved role entitlements</div>', unsafe_allow_html=True)

    search_col, department_col, role_col, status_col = st.columns([2, 1, 1.4, 1])
    with search_col:
        search = st.text_input("Search", placeholder="Name, Employee ID, or Email")
    with department_col:
        department_choice = st.selectbox("Department", ("All", *DEPARTMENT_NAMES))
    with role_col:
        available_roles = (
            tuple(role.name for role in roles_for_department(department_choice))
            if department_choice != "All"
            else ROLE_NAMES
        )
        role_choice = st.selectbox("Job Role", ("All", *available_roles))
    with status_col:
        status_choice = st.selectbox("Status", ("All", "ACTIVE", "DISABLED"))

    employees = list_employees(
        settings.database_path,
        search=search,
        department=None if department_choice == "All" else department_choice,
        job_role=None if role_choice == "All" else role_choice,
        status=None if status_choice == "All" else status_choice,
    )

    st.metric("Matching Employees", len(employees))
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
            "Select Employee Profile to Inspect",
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
        st.warning("No employees match the selected criteria.")


def render_access_matrix() -> None:
    st.markdown('<div class="section-title">Access Matrix</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Map job roles to groups, applications, and permissions</div>', unsafe_allow_html=True)

    matrix_tab, groups_tab, apps_tab, permissions_tab = st.tabs(
        ("Access Matrix", "Groups Catalog", "Applications Catalog", "Permissions Catalog")
    )
    with matrix_tab:
        st.dataframe(access_matrix_rows(), width="stretch", hide_index=True)
    with groups_tab:
        st.dataframe(
            [{"Group Name": name} for name in GROUP_NAMES], width="stretch", hide_index=True
        )
    with apps_tab:
        st.dataframe(
            [
                {"Application": item.name, "Sensitivity Level": item.sensitivity}
                for item in APPLICATIONS
            ],
            width="stretch",
            hide_index=True,
        )
    with permissions_tab:
        st.dataframe(
            [
                {"Permission": item.name, "Description": item.description}
                for item in PERMISSIONS
            ],
            width="stretch",
            hide_index=True,
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
    st.markdown("#### Identity Transition Preview")
    before = plan.before_employee
    before_label = (
        "Identity does not exist"
        if before is None
        else f"{before.department} · {before.job_role} · {before.status.value}"
    )
    after = plan.after_employee
    identity_col, arrow_col, result_col = st.columns([4, 1, 4])
    identity_col.info(f"**BEFORE**\n\n{before_label}")
    arrow_col.markdown("### →")
    result_col.success(
        f"**AFTER**\n\n{after.department} · {after.job_role} · {after.status.value}"
    )

    st.markdown("#### Access Adjustments")
    _access_columns(plan.to_remove)
    _access_columns(plan.to_add)

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
        f"✓ {result['operation'].title()} completed for {result['employee_id']} · "
        f"Correlation `{result['correlation_id']}`"
    )
    employee = get_employee(settings.database_path, result["employee_id"])
    if employee:
        render_employee_profile(employee)
    if st.button("Dismiss Result"):
        del st.session_state["last_jml_result"]
        st.rerun()


def _render_joiner() -> None:
    st.markdown("### ➕ Joiner · Onboard New Identity")
    st.caption("Onboard a new employee and grant role-approved access.")
    department = st.selectbox("Department", DEPARTMENT_NAMES, key="joiner_department")
    compatible_roles = tuple(role.name for role in roles_for_department(department))
    job_role = st.selectbox("Job Role", compatible_roles, key="joiner_role")
    display_name = st.text_input("Employee Full Name", key="joiner_name", placeholder="e.g. Panthil Shah")
    email = st.text_input(
        "Email Address", placeholder="e.g. panthil@example.iamconcen", key="joiner_email"
    )
    reason = st.text_input(
        "Business Reason", value="New employee onboarding", key="joiner_reason"
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
    st.markdown("### 🔄 Mover · Department or Role Change")
    active_employees = list_employees(settings.database_path, status="ACTIVE")
    employee_id = st.selectbox(
        "Select Employee",
        tuple(employee.employee_id for employee in active_employees),
        format_func=lambda identifier: next(
            f"{employee.display_name} · {identifier} ({employee.job_role})"
            for employee in active_employees
            if employee.employee_id == identifier
        ),
        key="mover_employee",
    )
    target_department = st.selectbox(
        "Target Department", DEPARTMENT_NAMES, key="mover_department"
    )
    target_roles = tuple(role.name for role in roles_for_department(target_department))
    target_role = st.selectbox("Target Job Role", target_roles, key="mover_role")
    reason = st.text_input(
        "Business Reason", value="Approved role transfer", key="mover_reason"
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
    st.markdown("### ❌ Leaver · Offboard Identity")
    active_employees = list_employees(settings.database_path, status="ACTIVE")
    employee_id = st.selectbox(
        "Select Employee to Offboard",
        tuple(employee.employee_id for employee in active_employees),
        format_func=lambda identifier: next(
            f"{employee.display_name} · {identifier} ({employee.job_role})"
            for employee in active_employees
            if employee.employee_id == identifier
        ),
        key="leaver_employee",
    )
    reason = st.text_input(
        "Termination Reason", value="Employment ended", key="leaver_reason"
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
    st.markdown('<div class="section-title">Identity Lifecycle Operations</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Manage Joiner, Mover, and Leaver identity lifecycle events with transaction safety</div>', unsafe_allow_html=True)
    
    _render_last_result()
    joiner_tab, mover_tab, leaver_tab, audit_tab = st.tabs(
        ("Joiner (Onboard)", "Mover (Transfer)", "Leaver (Offboard)", "Audit Timeline")
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
                    "Time": _format_audit_time(event.timestamp),
                    "Employee": event.target_identity,
                    "Activity": _format_audit_activity(event),
                    "Status": _format_audit_status(event.result),
                }
                for event in events
            ],
            width="stretch",
            hide_index=True,
        )


def render_access_review() -> None:
    st.markdown('<div class="section-title">Access Review</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Evaluate expected vs actual entitlements and remediate privilege creep</div>', unsafe_allow_html=True)
    
    if message := st.session_state.pop("access_review_message", None):
        st.success(message)

    reviews = review_all(settings.database_path)
    summary = review_summary(reviews)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Reviewed Identities", summary["identities"])
    c2.metric("Compliant", summary["compliant"])
    c3.metric("Findings", summary["findings"])
    c4.metric("Privileged Identities", summary["privileged"])

    non_compliant = [r for r in reviews if not r.compliant]
    if non_compliant:
        st.markdown("### Non-Compliant Access Findings")
        st.dataframe(
            [
                {
                    "Employee ID": r.employee.employee_id,
                    "Name": r.employee.display_name,
                    "Department": r.employee.department,
                    "Role": r.employee.job_role,
                    "Findings": len(r.findings),
                }
                for r in non_compliant
            ],
            width="stretch",
            hide_index=True,
        )


def _format_audit_time(timestamp, include_tz: bool = False) -> str:
    from datetime import datetime, timezone
    if timestamp is None:
        return "—"
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    local_dt = timestamp.astimezone()
    now = datetime.now().astimezone()
    time_str = local_dt.strftime("%I:%M %p").lstrip("0")
    if local_dt.date() == now.date():
        res = time_str
    else:
        month_day = local_dt.strftime("%b ") + str(local_dt.day)
        res = f"{month_day}, {time_str}"
    if include_tz:
        tz_name = local_dt.strftime("%Z")
        if tz_name:
            res = f"{res} ({tz_name})"
    return res


def _extract_entity_item(event) -> str:
    if event.new_state and event.new_state != "null" and not event.new_state.startswith("{"):
        return event.new_state
    if event.old_state and event.old_state != "null" and not event.old_state.startswith("{"):
        return event.old_state
    return ""


def _format_audit_activity(event) -> str:
    item = _extract_entity_item(event)
    action = event.action

    if action == "JOINER_COMPLETED":
        return "Employee onboarded"
    elif action == "MOVER_COMPLETED":
        return "Role or department updated"
    elif action == "LEAVER_COMPLETED":
        return "Employee offboarded"
    elif action == "ACCOUNT_DISABLED":
        return "Account disabled"
    elif action == "ACCESS_DENIED":
        return "Access denied"
    elif action == "PERMISSION_GRANTED":
        return f"{item} permission assigned" if item else "Permission assigned"
    elif action == "APPLICATION_GRANTED":
        return f"{item} access assigned" if item else "Application access assigned"
    elif action == "GROUP_GRANTED":
        return f"{item} group assigned" if item else "Security group assigned"
    elif action == "PERMISSION_REVOKED":
        return f"{item} permission removed" if item else "Permission removed"
    elif action == "APPLICATION_REVOKED":
        return f"{item} access removed" if item else "Application access removed"
    elif action == "GROUP_REVOKED":
        return f"{item} group removed" if item else "Security group removed"
    elif action == "IDENTITY_CREATED":
        return "Identity created"
    elif action == "IDENTITY_UPDATED":
        return "Identity updated"
    elif action == "SECURITY_CONTROL_CHECK":
        return "Security control check"
    else:
        if item:
            return f"{item} {action.replace('_', ' ').lower()}"
        return action.replace("_", " ").title()


def _format_audit_status(result: str) -> str:
    res = (result or "").upper()
    if res in {"SUCCESS", "SUCCESSFUL", "PASSED", "PASS"}:
        return "Successful"
    elif res in {"FAILED", "FAILURE"}:
        return "Failed"
    elif res in {"DENIED", "ACCESS_DENIED"}:
        return "Denied"
    return res.replace("_", " ").title()


def _format_actor(actor: str) -> str:
    if actor in {"simulation.operator", "operator", "system"}:
        return "IAM Admin"
    return actor


def render_security_audit() -> None:
    st.markdown('<div class="section-title">Security & Audit</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Recent identity and access activity</div>', unsafe_allow_html=True)

    summary = audit_statistics(settings.database_path)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Audit Events", summary["events"])
    c2.metric("Failed Control Checks", summary["failed"])
    c3.metric("Open Security Findings", summary["open_findings"])

    events = list_audit_events(settings.database_path, limit=100)
    
    # Main Clean Table (Time, Employee, Activity, Status)
    st.dataframe(
        [
            {
                "Time": _format_audit_time(event.timestamp),
                "Employee": event.target_identity,
                "Activity": _format_audit_activity(event),
                "Status": _format_audit_status(event.result),
            }
            for event in events
        ],
        width="stretch",
        hide_index=True,
    )

    # Technical Details interaction
    with st.expander("🔍 View details"):
        st.caption("Inspect raw technical audit logs and system actor details.")
        if events:
            selected_idx = st.selectbox(
                "Select audit event",
                range(len(events)),
                format_func=lambda i: f"{_format_audit_time(events[i].timestamp)} · {events[i].target_identity} · {_format_audit_activity(events[i])} [{events[i].result}]",
                key="security_audit_inspect_event"
            )
            ev = events[selected_idx]
            d_col1, d_col2 = st.columns(2)
            with d_col1:
                st.write(f"**Time (Local):** `{_format_audit_time(ev.timestamp, include_tz=True)}`")
                st.write(f"**Raw UTC Timestamp:** `{ev.timestamp.isoformat()}`")
                st.write(f"**Actor:** `{_format_actor(ev.actor)} ({ev.actor})`")
                st.write(f"**Target:** `{ev.target_identity}`")
                st.write(f"**Raw Action:** `{ev.action}`")
            with d_col2:
                st.write(f"**Result:** `{ev.result}`")
                st.write(f"**Correlation ID:** `{ev.correlation_id}`")
                st.write(f"**Reason:** `{ev.reason or 'N/A'}`")
                if ev.old_state != "null":
                    st.write(f"**Old State:** `{ev.old_state}`")
                if ev.new_state != "null":
                    st.write(f"**New State:** `{ev.new_state}`")


def _format_aws_action_human(action: str) -> str:
    m = {
        "s3:GetObject": "Read objects from S3",
        "s3:ListBucket": "View files in S3 bucket",
        "s3:DeleteObject": "Delete files from S3",
        "s3:PutObject": "Upload files to S3",
        "sts:AssumeRole": "Assume IAM role",
    }
    return m.get(action, action)


def _format_cloudtrail_event_human(event_name: str) -> str:
    m = {
        "GetObject": "File accessed",
        "AssumeRole": "Role assumed",
        "PutObject": "File uploaded",
        "DeleteObject": "File deleted",
        "ListBucket": "Bucket listed",
    }
    return m.get(event_name, event_name.replace("_", " ").title())


def _clean_aws_name(name: str) -> str:
    """Strip old CILAMP prefixes/names from displayed AWS names without changing backend objects."""
    if not name:
        return ""
    import re
    cleaned = re.sub(r'(?i)\bcilamp[-_]?', '', name)
    cleaned = re.sub(r'[-_]+', '-', cleaned).strip('-_')
    return cleaned or name


def _clean_arn(arn: str) -> str:
    """Clean CILAMP prefixes from ARNs for display."""
    if not arn:
        return ""
    import re
    return re.sub(r'(?i)cilamp[-_]?', '', arn)


def render_aws_access() -> None:
    st.markdown('<div class="section-title">AWS Access Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Inspect AWS roles, IAM policies, STS identities, S3 scopes, and CloudTrail audit logs</div>', unsafe_allow_html=True)
    
    if message := st.session_state.pop("aws_message", None):
        st.success(message)

    state = get_aws_sync_state(settings.database_path)
    cols = st.columns(4)
    cols[0].metric("AWS Connection", state.status)
    cols[1].metric("System Mode", settings.mode)
    cols[2].metric("AWS Account", settings.aws_account_label)
    cols[3].metric("Last Sync", _format_audit_time(state.last_synced_at) if state.last_synced_at else "Never")

    st.write(f"**AWS Profile:** `{settings.aws_profile or 'default'}` · **Region:** `{settings.aws_region}`")
    
    if st.button("Synchronize AWS IAM", type="primary", key="aws_sync"):
        try:
            correlation_id = synchronize_aws(settings)
            st.session_state["aws_message"] = "✓ AWS IAM data synchronized successfully"
            st.rerun()
        except (AwsConnectorError, AwsSafetyError) as error:
            st.error(str(error))

    resources = list_aws_resources(settings.database_path)
    roles = list_aws_roles(settings.database_path)
    policies = list_aws_policies(settings.database_path)
    bindings = list_aws_bindings(settings.database_path)
    events = list_aws_cloudtrail_events(settings.database_path)
    operations = list_aws_operations(settings.database_path)

    resources_tab, roles_tab, policies_tab, access_tab, sts_tab, audit_tab, operations_tab = st.tabs(
        ("Resources", "Roles", "Policies", "Effective Access", "STS Identity", "CloudTrail", "AWS Operations")
    )
    
    with resources_tab:
        st.metric("Resources in Scope", len(resources))
        st.dataframe([{"Resource": _clean_aws_name(x.name), "Type": x.resource_type, "Region": x.region} for x in resources], width="stretch", hide_index=True)
        with st.expander("🔍 View details"):
            st.dataframe([{"Name": _clean_aws_name(x.name), "Type": x.resource_type, "Region": x.region, "Technical ARN": _clean_arn(x.arn)} for x in resources], width="stretch", hide_index=True)

    with roles_tab:
        st.metric("IAM Roles", len(roles))
        st.dataframe(
            [
                {
                    "Role": _clean_aws_name(x.name),
                    "Purpose": "Developer S3 & STS Access" if "developer" in x.name.lower() else "AWS IAM Identity Role",
                    "Access Level": "Scoped / Least-Privilege" if "developer" in x.name.lower() else "Administrative",
                }
                for x in roles
            ],
            width="stretch",
            hide_index=True,
        )
        with st.expander("🔍 View details"):
            st.dataframe([{"Role": _clean_aws_name(x.name), "Path": _clean_arn(x.path), "Trusted Principal": ", ".join(x.trusted_principals), "Technical ARN": _clean_arn(x.arn)} for x in roles], width="stretch", hide_index=True)

    with policies_tab:
        rows = [
            {
                "Policy": _clean_aws_name(p.name),
                "Scope": p.source.replace("_", " ").title(),
                "Effect": "Allowed" if s.effect == "Allow" else "Denied",
                "Action": ", ".join(_format_aws_action_human(act) for act in s.actions),
            }
            for p in policies for s in p.statements
        ]
        st.metric("Policies", len(policies))
        st.dataframe(rows, width="stretch", hide_index=True)
        with st.expander("🔍 View details"):
            raw_rows = [{"Policy": _clean_aws_name(p.name), "Source": p.source, "Effect": s.effect, "Raw Actions": ", ".join(s.actions), "Resources": ", ".join(_clean_arn(r) for r in s.resources)} for p in policies for s in p.statements]
            st.dataframe(raw_rows, width="stretch", hide_index=True)

    with access_tab:
        st.markdown("### Effective Policy Evaluation")
        if roles and resources:
            role_arn = st.selectbox("Select IAM Role", tuple(x.arn for x in roles), format_func=lambda arn: _clean_aws_name(next(x.name for x in roles if x.arn == arn)), key="aws_role")
            resource_arn = st.selectbox("Select AWS Resource", tuple(x.arn for x in resources), format_func=lambda arn: _clean_aws_name(next(x.name for x in resources if x.arn == arn)), key="aws_resource")
            action = st.selectbox("Select Action", tuple(AWS_ACTION_LABELS), format_func=lambda value: _format_aws_action_human(value), key="aws_action")
            role = next(x for x in roles if x.arn == role_arn)
            resource = next(x for x in resources if x.arn == resource_arn)
            decision = evaluate_aws_access(role, resource, action, policies, bindings)
            if decision.decision == "ALLOWED":
                st.success("Access is allowed because this role has permission to perform this action.")
            elif decision.decision == "UNKNOWN":
                st.warning(f"UNKNOWN — {decision.rationale}")
            else:
                st.error("Access is denied because the required permission was not found or was explicitly denied.")
        else:
            st.info("Synchronize AWS to evaluate cached access.")

    with sts_tab:
        st.markdown("### Current AWS Identity")
        st.write("**Role:** IAM ConCen Audit Role")
        st.write(f"**Account:** `{settings.aws_account_id or '967598289855'}`")
        st.write("**Session:** IAM ConCen")
        with st.expander("🔍 View details"):
            caller_display = _clean_arn(state.caller_arn) if state.caller_arn else "Not synchronized"
            st.write(f"**Caller Identity ARN:** `{caller_display}`")

    with audit_tab:
        st.metric("CloudTrail Events", len(events))
        st.dataframe(
            [
                {
                    "Time": _format_audit_time(x.event_time),
                    "Event": _format_cloudtrail_event_human(x.event_name),
                    "Identity": _clean_aws_name(_format_actor(x.username)),
                    "Resource": _clean_aws_name(x.resource_name),
                }
                for x in events
            ],
            width="stretch",
            hide_index=True,
        )
        with st.expander("🔍 View details"):
            st.dataframe([{"Time": x.event_time.isoformat(), "Raw Event": x.event_name, "Identity": _clean_aws_name(x.username), "Resource": _clean_aws_name(x.resource_name), "Event ID": x.event_id} for x in events], width="stretch", hide_index=True)

    with operations_tab:
        st.success("✓ AWS IAM data synchronized successfully")
        st.dataframe(
            [
                {
                    "Time": _format_audit_time(x.timestamp),
                    "Action": x.action.replace("_", " ").title(),
                    "Target": _clean_aws_name(x.target),
                    "Result": _format_audit_status(x.result),
                    "Details": _clean_aws_name(x.details),
                }
                for x in operations
            ],
            width="stretch",
            hide_index=True,
        )
        with st.expander("🔍 View details"):
            st.dataframe([{"Time": _format_audit_time(x.timestamp, include_tz=True), "Raw Time": x.timestamp.isoformat(), "Action": x.action, "Target": _clean_aws_name(x.target), "Result": x.result, "Details": _clean_aws_name(x.details)} for x in operations], width="stretch", hide_index=True)


# Route selection
if page == "📊 Dashboard":
    render_overview()
elif page == "👥 Employees & Roles":
    render_organization_explorer()
elif page == "🔄 Join / Move / Leave":
    render_jml_operations()
elif page == "🔍 Access Review":
    render_access_review()
elif page == "🛡️ Security & Audit":
    render_security_audit()
elif page == "☁️ AWS Access":
    render_aws_access()
else:
    render_access_matrix()

st.caption("IAM ConCen • AWS Identity & Access Management")
