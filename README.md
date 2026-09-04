# CILAMP

**Cloud Identity Lifecycle & Access Management Platform**

CILAMP is a simulation-first Cloud/IAM portfolio project. It will demonstrate employee identity lifecycle management, RBAC, least privilege, access review, auditability, and later safe lab integrations with Microsoft Entra ID, Azure, and AWS.

The repository is currently at **Phase 5 — Microsoft Entra ID Integration**. It contains 500 deterministic fictional employees, JML/RBAC/security workflows, and an isolated Entra connector with local simulation plus guarded Microsoft Graph live-lab support. Simulation performs no cloud calls; this repository has not claimed a live tenant validation.

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

The tests validate configuration safety, organization/JML/RBAC behavior, security scenarios, the Graph adapter contract, Entra synchronization/cache behavior, live-write safety gates, audit evidence, and headless rendering of every dashboard page.

## Repository layout

```text
dashboard/           Streamlit IAM Command Center
src/cilamp/          Provider-independent identity, access, and data modules
tests/               Automated Phase 0 and Phase 1 checks
data/                Ignored local SQLite runtime data
docs/                Architecture, security, roadmap, and learning memory
```

Read `docs/PROJECT_STATE.md` for the exact project status and next approved task.

## Dashboard

- **Overview:** organization counts, department/role distributions, health, and roadmap.
- **Organization Explorer:** employee search, department/role/status filters, and access profiles.
- **JML Operations:** preview, confirm, and execute simulated Joiner, Mover, and Leaver changes with audit results.
- **Access Review:** inspect expected versus actual access, risk-rated findings, access sources, privileged identities, and confirmed remediation.
- **Security & Audit:** create controlled scenarios, filter findings/events, investigate identity timelines and privileged activity, and follow remediation checklists.
- **Microsoft Entra:** synchronize users/groups/service principals, inspect memberships and directory audit data, review connector operations, and preview confirmed simulation or allowlisted live-lab writes.
- **Access Matrix:** role → groups → applications → permissions, plus catalogs and privileged-role indicators.

## Optional dedicated Entra lab

Keep `CILAMP_MODE=SIMULATION` for normal demonstrations. For a dedicated lab, copy `.env.example` values into an ignored local `.env` or set them in the process environment, sign in with `az login --tenant <tenant-id>`, and set `CILAMP_MODE=LIVE_LAB` only after reviewing `docs/SECURITY_MODEL.md`. Live writes additionally require `CILAMP_ENTRA_WRITES_ENABLED=true`, an allowed UPN domain, an allowlist of group object IDs, and confirmation in the dashboard. CILAMP does not accept or store passwords, client secrets, or access tokens.
