# CILAMP — Project State

> This file is the repository source of truth. Read it at the start of every working session and update it before ending meaningful work.

## Project

**Name:** Cloud Identity Lifecycle & Access Management Platform

**Primary Focus:** Cloud IAM / Identity Lifecycle / Cloud Security / Cloud Operations

**Default Mode:** `SIMULATION`

## Current Status

**Current Phase:** Phase 3 — RBAC & Access Review

**Current Milestone:** Phase 3 access-review policy and remediation completed and locally validated

**Overall Status:** COMPLETE — waiting for the project owner to approve Phase 4

## Phase Status

| Phase | Name | Status |
|---|---|---|
| 0 | Project Foundation | COMPLETE |
| 1 | Organization & IAM Model | COMPLETE |
| 2 | Joiner-Mover-Leaver Engine | COMPLETE |
| 3 | RBAC & Access Review | COMPLETE |
| 4 | Security & Audit Center | NOT STARTED |
| 5 | Microsoft Entra ID Integration | NOT STARTED |
| 6 | Azure Identity & RBAC | NOT STARTED |
| 7 | AWS IAM Integration | NOT STARTED |
| 8 | Terraform / Infrastructure as Code | NOT STARTED |
| 9 | Docker & Operationalization | NOT STARTED |
| 10 | Unified IAM Command Center | NOT STARTED |

## Completed Work

### Phase 0

- Established the secure Git/Python/Streamlit/SQLite foundation, simulation-only mode, health checks, and repository memory.

### Phase 1

- Created six departments, ten roles, thirteen groups, ten applications, fourteen permissions, and exactly 500 deterministic fictional employees.
- Implemented role-derived expected access, organization persistence, search/filtering, employee profiles, and the visual Access Matrix.

### Phase 2

- Implemented confirmed, transactional Joiner, Mover, and Leaver workflows with actual assignments, removal-before-grant behavior, complete offboarding, stale-preview protection, and correlated lifecycle audit events.

### Phase 3

- Added a provider-independent RBAC policy engine that calculates expected access from role and identity status.
- Compares expected with independently persisted actual groups, applications, and permissions.
- Detects excessive privilege, unauthorized group/application access, stale permission/privilege creep, and missing access.
- Risk-rates privileged variance as `CRITICAL`, other excess/stale access as `HIGH`, and missing required access as `MEDIUM`.
- Identifies privileged identities through approved privileged roles or actual privileged assignments.
- Explains role/group-policy inheritance versus direct or stale assignments.
- Added the explicit Developer→`platform.administrator` mandatory security scenario with confirmation and audit evidence.
- Added confirmed, transactional remediation that removes excess access, restores missing expected access, preserves the role, and rejects stale reviews.
- Added the RBAC & Access Review Center with organization metrics, filters, review inventory, expected/actual/difference/source views, findings, explanations, suggested remediation, and privileged identity inventory.
- Added access-review metrics to Overview.

## In-Progress Work

None. Phase 3 is complete. Do not begin Phase 4 without explicit approval.

## Important Architecture State

```text
Role + identity status                  Actual assignments
         ↓                                      ↓
  Expected access ───────── policy compare ─ Actual access
                              ↓
       Risk-rated findings + source explanation
                              ↓ confirm
          Transactional least-privilege reconciliation
                              ↓
                 Correlated audit evidence
```

Policy evaluation is pure and contains no persistence or cloud-provider calls. Findings are derived from current state rather than stored as an independent truth. The audit foundation records lifecycle, scenario, and remediation evidence; Phase 4 owns the unified Security & Audit Center and troubleshooting scenarios.

## Important User Decisions

1. CILAMP remains Cloud/IAM-first and UI-first.
2. Work proceeds one explicitly approved phase at a time.
3. Expected policy and actual assignments remain separate.
4. Administrator access is never part of a normal-role baseline; the Phase 3 Administrator permission is simulation-only.
5. Security scenarios and remediation require explicit confirmation and audit evidence.
6. Findings must not be hidden merely to produce a green dashboard.
7. Stale reviews fail closed and must be refreshed.
8. No cloud integration or live write begins before its approved phase.

## Known Issues

### ISSUE-001 — Managed sandbox temporary-directory permissions

**Status:** DOCUMENTED

**Severity:** Low

**Description:** The managed Windows sandbox restricts cleanup of some Python-created temporary directories used internally by Streamlit's test framework.

**Impact:** None on application behavior or assertions; all 31 tests passed.

**Workaround:** Direct `TEMP`/`TMP` to an approved writable directory and remove inaccessible sandbox artifacts with appropriate workspace permission.

**Planned Fix:** No CILAMP product change required; workflow remains in `docs/TROUBLESHOOTING.md`.

## Test Status

**Last Test Run:** 2026-09-04

**Command:** `python -m pytest` with managed-sandbox `TEMP`/`TMP` directed to the project data directory

**Result:** 31 passed, 0 failed

**Coverage:** Phase 0–2 regression coverage plus compliant access, expected-access calculation, group-derived source explanation, Developer Administrator detection, risk levels, missing/stale/unauthorized access, privileged identity inventory, scenario audit, remediation, stale-review rejection, and all five dashboard pages

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

**Commit:** Pending Phase 3 milestone commit at the time of this state update

**Message:** `feat(phase-3): implement RBAC access review`

## Exact Next Recommended Task

Wait for the project owner to validate the Phase 3 dashboard and explicitly approve **Phase 4 — Security & Audit Center**. Phase 4 should unify lifecycle, policy, privileged, and failed-operation events; add filtering and identity timelines; implement the six required security/troubleshooting scenarios; and preserve truthful result states. Do not implement Phase 4 automatically.
