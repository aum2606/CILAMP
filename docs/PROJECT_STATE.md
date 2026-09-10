# CILAMP — Project State

> This file is the repository source of truth. Read it at the start of every working session and update it before ending meaningful work.

## Project

**Name:** Cloud Identity Lifecycle & Access Management Platform

**Primary Focus:** Cloud IAM / Identity Lifecycle / Cloud Security / Cloud Operations

**Default Mode:** `SIMULATION`

## Current Status

**Current Phase:** Phase 7 — AWS IAM Integration

**Current Milestone:** Phase 7 AWS IAM roles, policy evaluation, STS, S3, and CloudTrail completed and locally validated

**Overall Status:** COMPLETE — waiting for the project owner to validate Phase 7 and approve Phase 8

## Phase Status

| Phase | Name | Status |
|---|---|---|
| 0 | Project Foundation | COMPLETE |
| 1 | Organization & IAM Model | COMPLETE |
| 2 | Joiner-Mover-Leaver Engine | COMPLETE |
| 3 | RBAC & Access Review | COMPLETE |
| 4 | Security & Audit Center | COMPLETE |
| 5 | Microsoft Entra ID Integration | COMPLETE |
| 6 | Azure Identity & RBAC | COMPLETE |
| 7 | AWS IAM Integration | COMPLETE |
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

### Phase 6

- Added isolated Azure simulation and Azure Resource Manager read-only connectors.
- Modeled resource groups, storage accounts, Key Vault, application resources, human groups, service principals, and managed identities.
- Modeled Azure role assignments as principal + role definition + scope with parent-scope inheritance.
- Demonstrated management-plane versus data-plane authorization using Reader, Storage Blob Data Reader, and Key Vault Secrets User.
- Added provider-independent `ALLOWED`, `NOT GRANTED`, and `UNKNOWN` evaluation; unknown/custom/conditional roles do not produce false certainty.
- Added the mandatory no-secret comparison between a static-secret anti-pattern and managed identity → Azure RBAC → resource.
- Added resource-group-scoped live ARM discovery with external Azure Identity authentication, configured/token tenant matching, sanitized errors, and no Azure write endpoint.
- Added cached Azure resources, identities, role assignments, synchronization state, and append-only operations.
- Added Azure Access dashboard tabs for Resources, Identities, RBAC Assignments, Effective Access, Managed Identities, Credential Patterns, and Azure Operations.

### Phase 7

- Added isolated deterministic AWS simulation and optional boto3 read-only connector contracts.
- Modeled IAM roles, trust principals, managed and inline identity policies, policy statements, role-policy attachments, allowlisted S3 resources, STS caller identity, and selected CloudTrail metadata.
- Demonstrated a Developer role that can list one development bucket and read its objects, cannot administer IAM, cannot access unrelated resources, and is explicitly denied unnecessary object deletion.
- Added explainable `ALLOWED`, `EXPLICIT DENY`, `NOT GRANTED`, and `UNKNOWN` outcomes with wildcard action/resource matching and explicit-deny precedence.
- Kept evaluation conservative: resource policies, SCPs/RCPs, permissions boundaries, session policies, tags, and request context remain documented provider-side limitations.
- Added AWS account verification through `sts:GetCallerIdentity`, an unconditional root-identity rejection, IAM path restriction, explicit S3 bucket allowlist, sanitized SDK failures, and no AWS write methods.
- Added cached resources, roles, policies, attachments, CloudTrail event metadata, synchronization state, and append-only AWS operations. Raw CloudTrail payloads and credential values are never stored.
- Added an eight-tab AWS Access dashboard for Resources, Roles, Policies, Effective Access, STS Identity, CloudTrail, Credential Patterns, and AWS Operations.

## In-Progress Work

None. Phase 7 is complete. Do not begin Phase 8 without explicit approval.

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

The Security & Audit Center still separates audit evidence, current policy evaluation, and case status. Phase 7 adds an AWS boundary: simulation or read-only boto3 discovery → timestamped cache → conservative identity-policy explanation → AWS Access UI. The AWS adapter was not connected to a real account during development, so no live AWS success is claimed.

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
12. Azure live discovery is read-only and restricted to one explicitly configured resource group.
13. `NOT GRANTED` is not represented as an Azure deny assignment; custom or conditional evidence produces `UNKNOWN`.
14. The static-secret anti-pattern stores posture metadata only, never a credential value.
15. AWS live discovery requires a configured 12-digit lab account, rejects root, scopes role inventory by IAM path, and probes only allowlisted S3 buckets.
16. Cached AWS identity policies are teaching evidence, not a complete authorization oracle; external policy layers and request context stay explicit limitations.
17. Raw CloudTrail event JSON and AWS credentials are never cached or displayed.

## Known Issues

### ISSUE-001 — Managed sandbox temporary-directory permissions

**Status:** DOCUMENTED

**Severity:** Low

**Description:** The managed Windows sandbox restricts cleanup of some Python-created temporary directories used internally by Streamlit's test framework.

**Impact:** None on application behavior or assertions; all 72 tests passed across the dashboard and non-dashboard suites.

**Workaround:** Direct `TEMP`/`TMP` to an approved writable directory and remove inaccessible sandbox artifacts with appropriate workspace permission.

**Planned Fix:** No CILAMP product change required; workflow remains in `docs/TROUBLESHOOTING.md`.

## Test Status

**Last Test Run:** 2026-09-10

**Commands:** `python -m pytest -q` plus a live Streamlit health check

**Result:** 72 passed, 0 failed (71 non-dashboard + 1 full dashboard traversal)

**Coverage:** Phase 0–6 regression coverage plus AWS-only live guards, account/root verification, read-only call shape, IAM/S3 scoping, policy wildcard and explicit-deny behavior, narrow allowed/not-granted access, STS credential posture, CloudTrail metadata, AWS sync/cache counts, and all nine dashboard pages

**Dashboard Smoke Check:** Headless traversal rendered all nine pages and synchronized simulated Entra, Azure, and AWS data; Streamlit started on local port 8506 and `/_stcore/health` returned HTTP 200 `ok`

## Cloud Integration Status

| Integration | Status |
|---|---|
| Microsoft Entra ID | SIMULATION COMPLETE / LIVE LAB READY, NOT VALIDATED |
| Microsoft Graph | CONNECTOR IMPLEMENTED / NO LIVE CALL CLAIMED |
| Azure | SIMULATION COMPLETE / READ-ONLY LIVE LAB READY, NOT VALIDATED |
| AWS | SIMULATION COMPLETE / READ-ONLY LIVE LAB READY, NOT VALIDATED |
| Terraform | NOT CONFIGURED |
| Docker | NOT CONFIGURED |

`azure-identity` and `boto3` are declared for optional cloud authentication/discovery. Tests use fake credentials/SDK sessions, dashboard tests use simulation, and no cloud resource was read or modified.

## Last Relevant Git Commit

**Commit:** pending Phase 7 milestone commit

**Message:** `feat(phase-7): implement AWS IAM access center`

## Exact Next Recommended Task

Wait for the project owner to validate the Phase 7 dashboard. If a dedicated AWS lab is available, perform a separately supervised read-only synchronization with a least-privileged SSO/assume-role profile. Begin **Phase 8 — Terraform / Infrastructure as Code** only after explicit approval; do not implement it automatically.
