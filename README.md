# IAM ConCen

**Cloud Identity Lifecycle & Access Management Platform — AWS IAM Center**

IAM ConCen is a Cloud/IAM management platform. It demonstrates employee identity lifecycle management (JML), RBAC, least privilege, access reviews, auditability, and AWS IAM integrations.

## Quick start

Prerequisites: Python 3.11 or later.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m streamlit run dashboard/app.py
```

Open the local URL printed by Streamlit, normally <http://localhost:8501>.

## Verify the foundation

```powershell
python -m pytest
```

## Repository layout

```text
dashboard/           Streamlit IAM ConCen Command Center
src/cilamp/          Provider-independent identity, access, and data modules
tests/               Automated test suite
data/                Ignored local SQLite runtime data
```

## Dashboard Features

- **Overview:** Organization counts, department/role distributions, system health.
- **Organization Explorer:** Employee search, department/role/status filters, and access profiles.
- **JML Operations:** Preview, confirm, and execute simulated Joiner, Mover, and Leaver changes.
- **Access Review:** Inspect expected versus actual access, risk-rated findings, and remediation.
- **Security & Audit:** Controlled scenarios, audit events, and identity timeline investigation.
- **AWS Access:** Inspect roles, policies, allowlisted S3 resources, STS identity posture, and CloudTrail metadata.
- **Access Matrix:** Role → Groups → Applications → Permissions catalog.
