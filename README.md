# CILAMP

**Cloud Identity Lifecycle & Access Management Platform**

CILAMP is a simulation-first Cloud/IAM portfolio project. It will demonstrate employee identity lifecycle management, RBAC, least privilege, access review, auditability, and later safe lab integrations with Microsoft Entra ID, Azure, and AWS.

The repository is currently at **Phase 4 — Security & Audit Center**. It contains 500 deterministic fictional employees, JML and RBAC workflows, persisted security cases, six controlled IAM scenarios, unified audit views, guided troubleshooting, and confirmed simulation remediation. No cloud APIs are connected and no live resources are modified.

## Quick start

Prerequisites: Python 3.11 or later.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m streamlit run dashboard/app.py
```

Open the local URL printed by Streamlit, normally <http://localhost:8501>.

The dashboard creates a local SQLite database at `data/cilamp.db`. That runtime file and all `.env` files are ignored by Git.

## Verify the foundation

```powershell
python -m pytest
```

The tests validate configuration safety, organization/JML/RBAC behavior, all six security scenarios, truthful failed control checks, finding filters/status, remediation safety, audit evidence, repository behavior, and headless rendering of every dashboard page.

## Repository layout

```text
dashboard/           Streamlit IAM Command Center
src/cilamp/          Provider-independent identity, access, and data modules
tests/               Automated Phase 0 and Phase 1 checks
data/                Ignored local SQLite runtime data
docs/                Architecture, security, roadmap, and learning memory
```

Read `docs/PROJECT_STATE.md` for the exact project status and next approved task.

## Phase 1 dashboard

- **Overview:** organization counts, department/role distributions, health, and roadmap.
- **Organization Explorer:** employee search, department/role/status filters, and access profiles.
- **JML Operations:** preview, confirm, and execute simulated Joiner, Mover, and Leaver changes with audit results.
- **Access Review:** inspect expected versus actual access, risk-rated findings, access sources, privileged identities, and confirmed remediation.
- **Security & Audit:** create controlled scenarios, filter findings/events, investigate identity timelines and privileged activity, and follow remediation checklists.
- **Access Matrix:** role → groups → applications → permissions, plus catalogs and privileged-role indicators.
