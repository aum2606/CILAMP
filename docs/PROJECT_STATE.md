# CILAMP — Project State

> This file is the repository source of truth. Read it at the start of every working session and update it before ending meaningful work.

## Project

**Name:** Cloud Identity Lifecycle & Access Management Platform

**Primary Focus:** Cloud IAM / Identity Lifecycle / Cloud Security / Cloud Operations

**Default Mode:** `SIMULATION`

## Current Status

**Current Phase:** Phase 5 — Microsoft Entra ID Integration

**Current Milestone:** Phase 5 Entra simulation and guarded Microsoft Graph lab integration completed and locally validated

**Overall Status:** COMPLETE — waiting for the project owner to validate Phase 5 and approve Phase 6

## Phase Status

| Phase | Name | Status |
|---|---|---|
| 0 | Project Foundation | COMPLETE |
| 1 | Organization & IAM Model | COMPLETE |
| 2 | Joiner-Mover-Leaver Engine | COMPLETE |
| 3 | RBAC & Access Review | COMPLETE |
| 4 | Security & Audit Center | COMPLETE |
| 5 | Microsoft Entra ID Integration | COMPLETE |
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

### Phase 5

- Added an isolated Microsoft Entra connector contract with deterministic simulation and Microsoft Graph v1.0 implementations.
- Added Azure CLI authentication by default for local live labs and optional `DefaultAzureCredential` for managed/workload identity environments.
- Added cached users, groups, selected memberships, service principals, directory audits, synchronization state, and append-only Entra operations.
- Added an Entra dashboard page for connection state, mode, safe tenant label, synchronization, directory objects, application identities, audit data, operations, licensing guidance, and write readiness.
- Added guarded selected-user department/job-title updates and group membership add/remove operations.
- Required explicit live-lab enablement, configured tenant/token-tenant match, separate write enablement, synchronized targets, allowed UPN suffix, group allowlist, and UI confirmation.
- Kept simulation fully functional and ensured no password, client secret, certificate, or access token is accepted or persisted.
- Added safe partial capability behavior when directory audit retrieval is unavailable due to consent, role, retention, or licensing.
- Installed and declared `azure-identity` 1.25.3; tested Graph request construction with a fake credential and transport.

## In-Progress Work

None. Phase 5 is complete. Do not begin Phase 6 without explicit approval.

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

The Security & Audit Center still separates audit evidence, current policy evaluation, and case status. Phase 5 adds a provider boundary after the stable local IAM logic: an Entra service selects either a local simulation adapter or a tenant-pinned Microsoft Graph adapter, then stores a timestamped display cache and separate operation history. The Graph adapter is present but was not connected to a real tenant during development, so no live read or write success is claimed.

## Important User Decisions

1. CILAMP remains Cloud/IAM-first and UI-first.
2. Work proceeds one explicitly approved phase at a time.
3. Failed operations remain historically `FAILURE` after later remediation succeeds.
4. Security findings may change status, but audit events are append-only evidence.
5. Scenario and remediation actions require preview/confirmation and correlation IDs.
6. The workload-credential scenario stores no credential value.
7. Findings must not be hidden merely to produce a green dashboard.
8. No cloud integration or live write begins before its approved phase.
9. Entra live mode must be explicitly tenant-pinned and cannot be enabled solely from the dashboard.
10. Live Entra writes remain disabled by default and require target restrictions plus per-operation confirmation.
11. Mocked Graph tests validate the adapter contract, not real tenant consent, licensing, or execution.

## Known Issues

### ISSUE-001 — Managed sandbox temporary-directory permissions

**Status:** DOCUMENTED

**Severity:** Low

**Description:** The managed Windows sandbox restricts cleanup of some Python-created temporary directories used internally by Streamlit's test framework.

**Impact:** None on application behavior or assertions; all 47 tests passed across the dashboard and non-dashboard suites.

**Workaround:** Direct `TEMP`/`TMP` to an approved writable directory and remove inaccessible sandbox artifacts with appropriate workspace permission.

**Planned Fix:** No CILAMP product change required; workflow remains in `docs/TROUBLESHOOTING.md`.

## Test Status

**Last Test Run:** 2026-09-04

**Commands:** `python -m pytest -k "not dashboard"` and `python -m pytest tests/test_dashboard.py -vv`

**Result:** 47 passed, 0 failed (46 non-dashboard + 1 full dashboard traversal)

**Coverage:** Phase 0–4 regression coverage plus live-mode configuration guards, configured/token tenant matching, Graph v1 request/response translation, sanitized failures, no-token persistence, Entra sync/cache counts, membership reads, explicit confirmation, write-disable switch, allowed UPN domain, group allowlist, and all seven dashboard pages

**Dashboard Smoke Check:** Headless traversal rendered all seven pages and synchronized the simulated Entra directory; Streamlit also started on local port 8503 and `/_stcore/health` returned `ok`

## Cloud Integration Status

| Integration | Status |
|---|---|
| Microsoft Entra ID | SIMULATION COMPLETE / LIVE LAB READY, NOT VALIDATED |
| Microsoft Graph | CONNECTOR IMPLEMENTED / NO LIVE CALL CLAIMED |
| Azure | NOT CONNECTED |
| AWS | NOT CONNECTED |
| Terraform | NOT CONFIGURED |
| Docker | NOT CONFIGURED |

`azure-identity` is installed for optional authentication. Tests use fake credentials/transports, the dashboard smoke test uses simulation, and no cloud resource was read or modified.

## Last Relevant Git Commit

**Commit:** `bcdea7f`

**Message:** `feat(phase-5): implement guarded Microsoft Entra integration`

## Exact Next Recommended Task

Wait for the project owner to validate the Phase 5 dashboard. If a dedicated lab is available, perform a separately supervised read-only tenant validation before enabling any write. Begin **Phase 6 — Azure Identity & RBAC** only after explicit approval; do not implement it automatically.
