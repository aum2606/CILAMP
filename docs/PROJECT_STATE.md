# CILAMP — Project State

> This file is the repository source of truth. Read it at the start of every working session and update it before ending meaningful work.

## Project

**Name:** Cloud Identity Lifecycle & Access Management Platform

**Primary Focus:** Cloud IAM / Identity Lifecycle / Cloud Security / Cloud Operations

**Default Mode:** `SIMULATION`

## Current Status

**Current Phase:** Phase 2 — Joiner-Mover-Leaver Engine

**Current Milestone:** Phase 2 JML operations completed and locally validated

**Overall Status:** COMPLETE — waiting for the project owner to approve Phase 3

## Phase Status

| Phase | Name | Status |
|---|---|---|
| 0 | Project Foundation | COMPLETE |
| 1 | Organization & IAM Model | COMPLETE |
| 2 | Joiner-Mover-Leaver Engine | COMPLETE |
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

- Created six departments, ten roles, thirteen groups, ten applications, thirteen permissions, and exactly 500 deterministic fictional employees.
- Implemented role-derived expected access, organization persistence, search/filtering, employee profiles, and the visual Access Matrix.

### Phase 2

- Separated expected role access from actual persisted employee assignments.
- Added provider-independent Joiner, Mover, and Leaver preview plans.
- Added validation for role compatibility, fictional email format/uniqueness, employee status, and no-op moves.
- Added explicit access-to-remove and access-to-add calculations.
- Implemented removal-before-grant Mover execution, including cleanup of unjustified actual access.
- Implemented Leaver account disablement and complete assignment revocation while preserving the identity record.
- Added explicit UI confirmation before every simulated write.
- Added atomic SQLite execution and stale-preview rejection.
- Added structured audit events with timestamp, actor, target, action, old/new state, result, reason, event ID, and correlation ID.
- Added a JML Operations Console with Joiner, Mover, Leaver, result profile, and audit timeline views.
- Added lifecycle metrics to Overview and actual assignment display to employee profiles.
- Verified restart-safe offboarding: initialization does not restore revoked Leaver access.

## In-Progress Work

None. Phase 2 is complete. Do not begin Phase 3 without explicit approval.

## Important Architecture State

```text
Role catalog (expected access)       SQLite assignments (actual access)
                \                         /
                 Lifecycle plan + delta
                           ↓ preview
                    Explicit confirmation
                           ↓
             Transactional simulation execution
                           ↓
              Correlated lifecycle audit events
                           ↓
                 Streamlit result/profile
```

Lifecycle rules contain no Entra, Azure, or AWS calls. Actual-vs-expected access can now be evaluated in Phase 3. The audit foundation exists for lifecycle operations, while the full Security & Audit Center remains Phase 4.

## Important User Decisions

1. CILAMP remains Cloud/IAM-first and UI-first.
2. Work proceeds one explicitly approved phase at a time.
3. JML operations require preview and confirmation even in simulation mode.
4. Movers remove obsolete access before receiving new access.
5. Leavers retain identity/audit history but lose active access.
6. Stale lifecycle previews fail closed and must be regenerated.
7. Simulation must remain stable before live cloud integration.
8. No hardcoded secrets, broad production credentials, silent cloud writes, or fake live results.

## Known Issues

### ISSUE-001 — Managed sandbox temporary-directory permissions

**Status:** DOCUMENTED

**Severity:** Low

**Description:** The managed Windows sandbox restricts cleanup of some Python-created temporary directories used internally by Streamlit's test framework.

**Impact:** None on application behavior or assertions; all 23 tests passed.

**Workaround:** Direct `TEMP`/`TMP` to an approved writable directory and remove inaccessible sandbox artifacts with appropriate workspace permission.

**Planned Fix:** No CILAMP product change required; workflow remains in `docs/TROUBLESHOOTING.md`.

## Test Status

**Last Test Run:** 2026-09-04

**Command:** `python -m pytest` with managed-sandbox `TEMP`/`TMP` directed to the project data directory

**Result:** 23 passed, 0 failed

**Coverage:** Phase 0/1 regression coverage plus Joiner least privilege and audit, Mover revocation/grant differences and order, excessive-access cleanup, Leaver disable/revoke/preservation, duplicate/no-op/disabled validation, lifecycle counts, and all four dashboard pages

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

**Commit:** `ac7911b`

**Message:** `feat(phase-2): implement JML lifecycle operations`

## Exact Next Recommended Task

Wait for the project owner to validate the Phase 2 dashboard and explicitly approve **Phase 3 — RBAC & Access Review**. Phase 3 should compare expected role access with actual assignments, flag excessive/stale/unauthorized access and privilege creep, explain violations visually, and support simulation remediation. Do not implement Phase 3 automatically.
