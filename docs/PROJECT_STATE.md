# CILAMP — Project State

> This file is the repository source of truth. Read it at the start of every working session and update it before ending meaningful work.

## Project

**Name:** Cloud Identity Lifecycle & Access Management Platform

**Primary Focus:** Cloud IAM / Identity Lifecycle / Cloud Security / Cloud Operations

**Default Mode:** `SIMULATION`

## Current Status

**Current Phase:** Phase 4 — Security & Audit Center

**Current Milestone:** Phase 4 security operations, audit, and troubleshooting completed and locally validated

**Overall Status:** COMPLETE — waiting for the project owner to approve Phase 5

## Phase Status

| Phase | Name | Status |
|---|---|---|
| 0 | Project Foundation | COMPLETE |
| 1 | Organization & IAM Model | COMPLETE |
| 2 | Joiner-Mover-Leaver Engine | COMPLETE |
| 3 | RBAC & Access Review | COMPLETE |
| 4 | Security & Audit Center | COMPLETE |
| 5 | Microsoft Entra ID Integration | NOT STARTED |
| 6 | Azure Identity & RBAC | NOT STARTED |
| 7 | AWS IAM Integration | NOT STARTED |
| 8 | Terraform / Infrastructure as Code | NOT STARTED |
| 9 | Docker & Operationalization | NOT STARTED |
| 10 | Unified IAM Command Center | NOT STARTED |

## Completed Work

### Phase 0

- Established the secure Python/Streamlit/SQLite foundation, simulation-only mode, health checks, Git workflow, and repository memory.

### Phase 1

- Created the deterministic 500-employee organization, IAM catalogs, expected role access, search/filtering, profiles, and Access Matrix.

### Phase 2

- Implemented confirmed, transactional JML workflows with actual assignments, removal-before-grant behavior, complete offboarding, stale-preview protection, and correlated lifecycle audit events.

### Phase 3

- Implemented expected-versus-actual RBAC evaluation, risk-rated findings, privileged identities, source explanations, the Developer Administrator scenario, and confirmed policy remediation.

### Phase 4

- Added persistent security findings with `OPEN` and `REMEDIATED` workflow states.
- Kept append-only audit evidence separate from derived access reviews and mutable case status.
- Implemented all six required controlled scenarios:
  1. Excessive privilege.
  2. Retained old-department access.
  3. Disabled identity with application access.
  4. Unauthorized group membership.
  5. Insecure workload credential metadata, with no secret value stored.
  6. Missing required application access.
- Added preview and explicit confirmation before each scenario changes local state.
- Recorded each observed failed control/access check truthfully as `FAILURE` and scenario creation as a separate successful action.
- Added security evidence, recommendations, correlation IDs, and scenario-specific troubleshooting checklists.
- Implemented confirmed remediation for human and workload cases while preserving historical failure events.
- Added Security & Audit dashboard tabs for Scenario Lab, Security Findings, Audit Events, Identity Timeline, Privileged Activity, and Troubleshooting.
- Added audit category/result/search filters and security/audit metrics to Overview.

## In-Progress Work

None. Phase 4 is complete. Do not begin Phase 5 without explicit approval.

## Important Architecture State

```text
Current role/access evaluation ── derived Access Review

Confirmed security scenario ─┬─ append-only Audit Events
                             └─ persisted Security Finding (OPEN)
                                              ↓ troubleshoot/confirm
                                  policy or posture remediation
                                              ↓
                              new audit evidence + REMEDIATED status
```

The Security & Audit Center unifies views without merging their responsibilities. Audit events state what happened, access reviews state what current policy sees, and security findings track case workflow. All connectors remain absent; every scenario and remediation is local simulation.

## Important User Decisions

1. CILAMP remains Cloud/IAM-first and UI-first.
2. Work proceeds one explicitly approved phase at a time.
3. Failed operations remain historically `FAILURE` after later remediation succeeds.
4. Security findings may change status, but audit events are append-only evidence.
5. Scenario and remediation actions require preview/confirmation and correlation IDs.
6. The workload-credential scenario stores no credential value.
7. Findings must not be hidden merely to produce a green dashboard.
8. No cloud integration or live write begins before its approved phase.

## Known Issues

### ISSUE-001 — Managed sandbox temporary-directory permissions

**Status:** DOCUMENTED

**Severity:** Low

**Description:** The managed Windows sandbox restricts cleanup of some Python-created temporary directories used internally by Streamlit's test framework.

**Impact:** None on application behavior or assertions; all 40 tests passed across the dashboard and non-dashboard suites.

**Workaround:** Direct `TEMP`/`TMP` to an approved writable directory and remove inaccessible sandbox artifacts with appropriate workspace permission.

**Planned Fix:** No CILAMP product change required; workflow remains in `docs/TROUBLESHOOTING.md`.

## Test Status

**Last Test Run:** 2026-09-04

**Commands:** `python -m pytest -k "not dashboard"` and `python -m pytest tests/test_dashboard.py -vv`

**Result:** 40 passed, 0 failed (39 non-dashboard + 1 full dashboard traversal)

**Coverage:** Phase 0–3 regression coverage plus all six scenario definitions/state changes, no-secret workload evidence, finding persistence/filtering, failed control results, remediation/audit preservation, troubleshooting steps, and all six dashboard pages

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

**Commit:** `2d29e52`

**Message:** `feat(phase-4): implement security and audit center`

## Exact Next Recommended Task

Wait for the project owner to validate the Phase 4 dashboard and explicitly approve **Phase 5 — Microsoft Entra ID Integration**. Phase 5 must begin with a safe lab-readiness and licensing/permission assessment, preserve simulation mode, isolate Microsoft Graph behind a connector, and require explicit confirmation for supported lab writes. Do not implement Phase 5 automatically.
