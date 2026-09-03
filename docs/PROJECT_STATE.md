# CILAMP — Project State

> This file is the repository source of truth. Read it at the start of every working session and update it before ending meaningful work.

## Project

**Name:** Cloud Identity Lifecycle & Access Management Platform

**Primary Focus:** Cloud IAM / Identity Lifecycle / Cloud Security / Cloud Operations

**Default Mode:** `SIMULATION`

## Current Status

**Current Phase:** Phase 0 — Project Foundation

**Current Milestone:** Phase 0 foundation completed and locally validated

**Overall Status:** COMPLETE — waiting for the project owner to approve Phase 1

## Phase Status

| Phase | Name | Status |
|---|---|---|
| 0 | Project Foundation | COMPLETE |
| 1 | Organization & IAM Model | NOT STARTED |
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

- Initialized the Git repository and persistent agent instructions.
- Added secure ignore rules and a placeholder-only `.env.example`.
- Established the installable Python package and dependency definitions.
- Added simulation-only configuration validation that fails closed for live mode.
- Added idempotent SQLite initialization, schema metadata, an empty employee store, and a health check.
- Added the Streamlit Project Control Center with phase, mode, health, employee count, module status, cloud status, and milestones.
- Added seven automated checks covering configuration, SQLite, project status, and a headless dashboard render.
- Added startup instructions and updated architecture, security, decision, learning, demo, and troubleshooting documentation.
- Verified a real Streamlit server start and an `ok` response from its health endpoint.

## In-Progress Work

None. Phase 0 is complete. Do not begin Phase 1 without explicit approval.

## Important Architecture State

```text
Streamlit Project Control Center
          ↓
Simulation-only configuration boundary
          ↓
SQLite initialization and health
```

The current package contains only foundation support modules. Domain, lifecycle, RBAC, audit, and cloud connector packages are intentionally deferred until their approved phases. Provider-specific APIs must remain separate from future lifecycle and policy logic.

## Important User Decisions

1. CILAMP remains Cloud/IAM-first and UI-first.
2. Work proceeds one approved phase at a time.
3. Simulation must be stable before live cloud integration.
4. No hardcoded secrets, broad production credentials, silent cloud writes, or fake live results.
5. The repository—not chat memory—is the long-term source of truth.
6. Phase 0 must stop before Phase 1 begins.

## Known Issues

### ISSUE-001 — Managed sandbox temporary-directory permissions

**Status:** DOCUMENTED

**Severity:** Low

**Description:** The managed Windows sandbox restricted Python-created temporary directories during test cleanup.

**Impact:** None on application behavior; all seven tests passed.

**Workaround:** Keep test artifacts and `TEMP`/`TMP` inside an approved writable directory when running in a similarly restricted environment.

**Planned Fix:** No product change required; retain the workflow in `docs/TROUBLESHOOTING.md`.

## Test Status

**Last Test Run:** 2026-09-03

**Command:** `python -m pytest` with `TEMP`/`TMP` directed to the writable project data directory for the managed sandbox

**Result:** 7 passed, 0 failed

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

**Commit:** Pending Phase 0 milestone commit at the time of this state update

**Message:** `feat(phase-0): establish project foundation`

## Exact Next Recommended Task

Wait for the project owner to validate the Phase 0 dashboard and explicitly approve **Phase 1 — Organization & IAM Model**. Phase 1 should then model approximately 500 fictional employees, departments, roles, groups, applications, permissions, and a visual access matrix. Do not implement Phase 1 automatically.
