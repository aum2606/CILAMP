"""CILAMP Phase 0 Project Control Center."""

from __future__ import annotations

import platform

import streamlit as st

from cilamp import __version__
from cilamp.config import load_settings
from cilamp.database import check_database
from cilamp.project_status import (
    CURRENT_PHASE,
    MODULE_STATUSES,
    PROJECT_NAME,
    PROJECT_SHORT_NAME,
    RECENT_MILESTONES,
    completed_module_count,
)


st.set_page_config(
    page_title="CILAMP | Project Control Center",
    page_icon="🛡️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem;}
    .cilamp-banner {
        padding: 1.4rem 1.6rem;
        border: 1px solid #23456b;
        border-radius: 14px;
        background: linear-gradient(120deg, #0c1b2a, #12395a);
        margin-bottom: 1.2rem;
    }
    .cilamp-banner h1 {color: #f4f8fb; margin: 0; font-size: 2.1rem;}
    .cilamp-banner p {color: #bcd3e8; margin: .35rem 0 0;}
    .mode-pill {
        display: inline-block; padding: .25rem .7rem; border-radius: 999px;
        background: #0d6b4d; color: white; font-weight: 700; letter-spacing: .04em;
    }
    .phase-note {
        border-left: 4px solid #3e8ed0; padding: .65rem 1rem;
        background: rgba(62, 142, 208, .08); border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

settings = load_settings()
database = check_database(settings.database_path)

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
    st.markdown(f'<div class="phase-note"><strong>{CURRENT_PHASE}</strong><br>Safe local foundation; no cloud connections or live writes.</div>', unsafe_allow_html=True)

st.subheader("System health")
health_col, db_col, employees_col, version_col = st.columns(4)
health_col.metric("Application", "HEALTHY")
db_col.metric("SQLite database", database.status)
employees_col.metric("Employees", database.employee_count, help="Employee data is introduced in Phase 1.")
version_col.metric("Foundation build", f"v{__version__}")

if database.healthy:
    st.success(f"Database ready · schema v{database.schema_version} · {database.message}")
else:
    st.error(database.message)

st.subheader("IAM capability roadmap")
status_rows = [
    {"Module": item.module, "Status": item.status, "IAM purpose": item.purpose}
    for item in MODULE_STATUSES
]
st.dataframe(status_rows, width="stretch", hide_index=True)

summary_col, cloud_col = st.columns(2)
with summary_col:
    st.subheader("Foundation summary")
    st.metric("Completed future modules", completed_module_count(), help="Phase 0 establishes the platform; IAM modules begin in Phase 1.")
    st.markdown(
        "- **Database:** local SQLite simulation store\n"
        "- **Dashboard:** Streamlit control center\n"
        "- **Security:** secrets excluded; simulation enforced\n"
        "- **Architecture:** provider-independent core"
    )

with cloud_col:
    st.subheader("Cloud integration")
    st.info(
        "Microsoft Entra ID, Azure, and AWS are **not connected**. "
        "Cloud integration begins only after local IAM logic is stable and a later phase is approved."
    )

st.subheader("Recent development milestones")
for milestone in RECENT_MILESTONES:
    st.markdown(f"✓ {milestone}")

with st.expander("Runtime details"):
    st.write(
        {
            "Python": platform.python_version(),
            "Database engine": "SQLite",
            "Schema version": database.schema_version,
            "Mode": settings.mode,
        }
    )

st.caption("CILAMP Phase 0 · Cloud/IAM-first · Simulation-only")
