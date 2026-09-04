# CILAMP — Project State

> This file is the repository source of truth. Read it at the start of every working session and update it before ending meaningful work.

## Project

**Name:** Cloud Identity Lifecycle & Access Management Platform

**Primary Focus:** Cloud IAM / Identity Lifecycle / Cloud Security / Cloud Operations

**Default Mode:** `SIMULATION`

## Current Status

**Current Phase:** Phase 1 — Organization & IAM Model

**Current Milestone:** Phase 1 organization model completed and locally validated

**Overall Status:** COMPLETE — waiting for the project owner to approve Phase 2

## Phase Status

| Phase | Name | Status |
|---|---|---|
| 0 | Project Foundation | COMPLETE |
| 1 | Organization & IAM Model | COMPLETE |
| 2 | Joiner-Mover-Leaver Engine | NOT STARTED |
| 3 | RBAC & Access Review | NOT STARTED |
| 4 | Security & Audit Center | NOT STARTED |
| 5 | Microsoft Entra ID Integration | NOT STARTED |
| 6 | Azure Identity & RBAC | NOT STARTED |
| 7 | AWS IAM Integration | NOT STARTED |
| 8 | Terraform / Infrastructure as Code | NOT STARTED |
| 9 | Docker & Operationalization | NOT STARTED |
| 10 | Unified IAM Command Center | NOT STARTED |

## Completed Work

### Phase 0

- Established the secure Git/Python/Streamlit/SQLite foundation and repository memory.
- Enforced simulation-only configuration and verified application/database health.

### Phase 1

- Defined provider-independent employee, department, job-role, group, application, permission, and effective-access objects.
- Created an authoritative catalog containing six departments, ten job roles, thirteen groups, ten applications, and thirteen permissions.
- Created a deterministic distribution of exactly 500 unique fictional active employees.
- Enforced department/role compatibility and role-derived access.
- Added schema version 2 and a non-destructive migration from the Phase 0 employee table.
- Added normalized SQLite catalog/mapping tables and idempotent organization seeding.
- Added parameterized employee search plus department, role, and status filters.
- Added Overview, Organization Explorer, employee profile, and Access Matrix views.
- Marked privileged roles and documented that application assignment is distinct from administrative permission.
- Verified the entire Phase 1 UI through headless page tests and a live Streamlit health check.

## In-Progress Work

None. Phase 1 is complete. Do not begin Phase 2 without explicit approval.

## Important Architecture State

```text
Fictional HR source / deterministic seed
                 ↓
Provider-independent identity + IAM catalog
                 ↓
Normalized SQLite organization repository
                 ↓
Search / filters / role-derived effective access
                 ↓
Streamlit Overview + Organization Explorer + Access Matrix
```

Expected access is currently calculated from a single authoritative role catalog. Direct grants, actual-vs-expected access, JML operations, and audit events are intentionally not implemented yet. Provider-specific APIs remain absent.

## Important User Decisions

1. CILAMP remains Cloud/IAM-first and UI-first.
2. Work proceeds one explicitly approved phase at a time.
3. Phase 1 uses deterministic fictional data rather than real identities or random access.
4. Access comes from department-compatible job roles, with groups preferred over direct grants.
5. Simulation must be stable before live cloud integration.
6. No hardcoded secrets, broad production credentials, silent cloud writes, or fake live results.
7. The repository—not chat memory—is the long-term source of truth.

## Known Issues

### ISSUE-001 — Managed sandbox temporary-directory permissions

**Status:** DOCUMENTED

**Severity:** Low

**Description:** The managed Windows sandbox restricts cleanup of some Python-created temporary directories used internally by Streamlit's test framework.

**Impact:** None on application behavior or assertions; all 15 tests passed.

**Workaround:** Direct `TEMP`/`TMP` to an approved writable directory and remove inaccessible sandbox artifacts with appropriate workspace permission.

**Planned Fix:** No CILAMP product change required; workflow remains in `docs/TROUBLESHOOTING.md`.

## Test Status

**Last Test Run:** 2026-09-04

**Command:** `python -m pytest` with managed-sandbox `TEMP`/`TMP` directed to the project data directory

**Result:** 15 passed, 0 failed

**Coverage:** Configuration safety, schema migration, database health, IAM catalog integrity, least-privilege exclusions, deterministic employee generation, role compatibility, organization persistence/idempotency, filters, effective access, and all three dashboard pages

**Dashboard Smoke Check:** Streamlit started on local port 8502; `/_stcore/health` returned `ok`

## Cloud Integration Status

| Integration | Status |
|---|---|
| Microsoft Entra ID | NOT CONNECTED |
| Microsoft Graph | NOT CONNECTED |
| Azure | NOT CONNECTED |
| AWS | NOT CONNECTED |
| Terraform | NOT CONFIGURED |
| Docker | NOT CONFIGURED |

No cloud SDK is invoked and no cloud resource was read or modified.

## Last Relevant Git Commit

**Commit:** `a3b1a7f`

**Message:** `feat(phase-1): implement organization and IAM model`

## Exact Next Recommended Task

Wait for the project owner to validate the Phase 1 dashboard and explicitly approve **Phase 2 — Joiner-Mover-Leaver Engine**. Phase 2 should use this role catalog to preview and execute simulated joiner, mover, and leaver operations with before/after access changes and audit records. Do not implement Phase 2 automatically.
