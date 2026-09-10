# CILAMP — Development Roadmap

## Project Goal

Build a portfolio-grade **Cloud Identity Lifecycle & Access Management Platform** that demonstrates enterprise IAM, Joiner-Mover-Leaver lifecycle management, RBAC, least privilege, security monitoring, non-human identities, multi-cloud access management, automation, and troubleshooting.

The project must be built progressively. Every phase must produce a visible and testable result.

---

# Status Legend

- `NOT STARTED`
- `IN PROGRESS`
- `BLOCKED`
- `COMPLETE`

---

# Phase 0 — Project Foundation

**Status:** COMPLETE

## Goal

Establish a clean, secure, version-controlled application foundation.

## Deliverables

- Git repository initialized.
- Secure `.gitignore`.
- `.env.example`.
- Python environment and dependencies.
- Modular source structure.
- SQLite initialization.
- Streamlit application skeleton.
- Project Control Center dashboard.
- Smoke tests.
- `AGENTS.md`.
- `CLAUDE.md`.
- Project documentation.
- Git milestone commit.

## Dashboard Requirements

Display:

- CILAMP project name.
- Current mode: `SIMULATION`.
- Current phase.
- Application health.
- Database health.
- Module status.
- Cloud integration status.
- Recent development milestone.

## Acceptance Criteria

- [x] Application launches successfully.
- [x] Dashboard is visible and passes a headless render check.
- [x] Database initializes successfully.
- [x] Basic smoke tests pass.
- [x] No secrets committed.
- [x] Documentation exists.
- [x] Project state is updated.
- [x] Git working tree is clean after milestone commit.

---

# Phase 1 — Organization & IAM Model

**Status:** COMPLETE

## Goal

Model a fictional enterprise with approximately 500 employees and define who should have access to what.

## Core Objects

- Employee
- Department
- Job Role
- Group
- Application
- Permission
- Access Rule

## Suggested Departments

- Engineering
- Finance
- HR
- Sales
- IT
- Marketing

## Example Roles

- Developer
- Engineering Manager
- Finance Analyst
- Finance Manager
- HR Administrator
- Sales User
- Sales Manager
- IT Administrator
- Security Administrator
- Marketing User

## Deliverables

- Generate 500 fictional employees.
- Department model.
- Role model.
- Group model.
- Application model.
- Access matrix.
- Employee profile page.
- Organization Explorer UI.
- Search and filters.

## Dashboard Requirements

Display:

- Employee count.
- Department distribution.
- Role distribution.
- Groups.
- Applications.
- Access matrix.
- Employee profile.

## Acceptance Criteria

- [x] 500 fictional employees exist.
- [x] Every employee has valid department/role/status.
- [x] Roles map to appropriate access.
- [x] Unrelated access is not granted by default.
- [x] Search and filters work.
- [x] Access matrix is visually inspectable.
- [x] Tests validate model rules.
- [x] Git milestone committed.

---

# Phase 2 — Joiner-Mover-Leaver Engine

**Status:** COMPLETE

## Goal

Implement employee identity lifecycle management.

## Joiner Workflow

- Create employee identity.
- Assign department.
- Assign role.
- Assign groups.
- Assign applications.
- Assign permissions.
- Create audit events.

## Mover Workflow

- Compare current vs desired access.
- Remove obsolete permissions first.
- Remove old groups.
- Remove obsolete applications.
- Assign new department/role.
- Grant new required access.
- Validate least privilege.
- Create audit events.

## Leaver Workflow

- Disable account.
- Remove active access.
- Remove group memberships.
- Revoke applications.
- Revoke permissions.
- Preserve employee/audit history.

## Dashboard Requirements

Create **JML Operations Console** with:

- Joiner form.
- Mover form.
- Leaver form.
- Before/after access comparison.
- Confirmation steps.
- Operation result.
- Audit timeline.

## Acceptance Criteria

- [x] Joiner receives expected access.
- [x] Joiner receives no unrelated access.
- [x] Mover loses old access.
- [x] Mover receives correct new access.
- [x] Privilege creep is prevented.
- [x] Leaver is disabled.
- [x] Leaver access is removed.
- [x] Audit records exist.
- [x] Tests pass.
- [x] Git milestone committed.

---

# Phase 3 — RBAC & Access Review

**Status:** COMPLETE

## Goal

Build an authorization/policy engine capable of detecting excessive, stale, or incorrect access.

## Capabilities

- Expected access calculation.
- Actual access calculation.
- Effective permission view.
- Group-derived access.
- Excess privilege detection.
- Unauthorized access detection.
- Privilege creep detection.
- Stale access detection.
- Privileged identity identification.

## Dashboard Requirements

Create **Access Review Center** displaying:

- Expected access.
- Actual access.
- Access differences.
- Violations.
- Risk level.
- Suggested remediation.
- Simulated remediation action.

## Mandatory Security Scenario

Developer receives Administrator permission.

The system must flag it as excessive privilege.

## Acceptance Criteria

- [x] Policy evaluator works.
- [x] Valid access is accepted.
- [x] Excessive access is detected.
- [x] Expected vs actual access is visible.
- [x] Remediation works in simulation mode.
- [x] Tests pass.
- [x] Git milestone committed.

---

# Phase 4 — Security & Audit Center

**Status:** COMPLETE

## Goal

Build auditable identity operations and security troubleshooting workflows.

## Audit Fields

- Timestamp.
- Actor.
- Target identity.
- Action.
- Old state.
- New state.
- Result.
- Reason.
- Event/correlation ID where useful.

## Security Scenarios

1. Excessive privilege.
2. Old department access retained after a move.
3. Disabled employee still has application access.
4. Unauthorized group membership.
5. Simulated insecure workload credential.
6. User unable to access required application.

## Dashboard Requirements

Create **Security & Audit Center** with:

- Recent lifecycle events.
- Security violations.
- Failed operations.
- Privileged activity.
- Filters.
- Identity timeline.
- Troubleshooting assistant/checklist.

## Acceptance Criteria

- [x] Important operations create audit events.
- [x] Security scenarios are visible.
- [x] Failed actions are represented accurately.
- [x] Troubleshooting path is documented.
- [x] Tests pass.
- [x] Git milestone committed.

---

# Phase 5 — Microsoft Entra ID Integration

**Status:** COMPLETE

## Goal

Connect stable local IAM logic to a dedicated Microsoft Entra lab.

## Capabilities

Where licensing and lab permissions permit:

- Read users.
- Read groups.
- Read memberships.
- Create/update selected lab users.
- Manage selected group memberships.
- Inspect service principals.
- Demonstrate application identity concepts.
- Retrieve relevant audit/sign-in information where feasible.

## Operating Modes

- `SIMULATION`
- `LIVE LAB`

## Dashboard Requirements

Create **Microsoft Entra** page displaying:

- Connection status.
- Current mode.
- Synced users.
- Groups.
- Application identities.
- Last synchronization.
- Recent Entra operations.

## Licensing Rule

If a feature is unavailable due to licensing:

- Do not fake live success.
- Demonstrate in simulation mode.
- Explain required enterprise licensing.
- Document expected enterprise behavior.

## Acceptance Criteria

- [x] Entra connector is isolated from domain logic.
- [x] Read operations work safely through simulation and a mocked Graph contract; live tenant validation remains environment-dependent and is not claimed.
- [x] Approved lab write operations are implemented with explicit confirmation, a separate enable switch, UPN-domain restriction, and group allowlist; no live write was executed during development.
- [x] No credentials are committed.
- [x] Simulation remains functional.
- [x] Git milestone committed.

---

# Phase 6 — Azure Identity & RBAC

**Status:** COMPLETE

## Goal

Demonstrate Azure resource authorization and non-human identity.

## Lab Resources

Possible examples:

- Resource Group.
- Storage Account.
- Key Vault.
- Managed Identity.

## Capabilities

- Azure RBAC assignment representation.
- Effective scope display.
- Least-privilege resource access.
- Managed Identity demonstration.
- Service identity comparison.

## Mandatory Demonstration

**Bad Pattern**

```text
Application
  ↓
Hardcoded Secret
  ↓
Azure Resource
```

**Preferred Pattern**

```text
Application
  ↓
Managed Identity
  ↓
Azure RBAC
  ↓
Azure Resource
```

No real secret should ever be committed for demonstration.

## Dashboard Requirements

Create **Azure Access** page displaying:

- Resources.
- Identities.
- RBAC assignments.
- Scope.
- Effective access.
- Managed identities.
- Allowed and denied access.

## Acceptance Criteria

- [x] Azure resources, identities, role definitions, assignments, and scope hierarchy are represented correctly in simulation and through a mocked ARM contract.
- [x] Least privilege is demonstrated with management/data-plane separation and ALLOWED, NOT GRANTED, and UNKNOWN outcomes.
- [x] Managed identity and credential-free workload access are visible.
- [x] No sensitive credentials are stored; the bad pattern is metadata and explanation only.
- [x] Git milestone committed.

---

# Phase 7 — AWS IAM Integration

**Status:** NOT STARTED

## Goal

Apply the same IAM principles to AWS.

## Capabilities

- IAM roles.
- IAM policies.
- Resource permissions.
- STS concepts.
- S3 access example.
- CloudTrail/audit representation.

## Example

Developer Role:

Allowed:

- Read selected S3 objects.

Not granted:

- IAM administration.
- Full account administration.
- Unnecessary delete operations.

## Dashboard Requirements

Create **AWS Access** page displaying:

- Roles.
- Policies.
- Resources.
- Effective permissions.
- Allowed actions.
- Denied/not-granted actions.
- Audit information where available.

## Acceptance Criteria

- [ ] AWS access model follows least privilege.
- [ ] Root credentials are never used.
- [ ] Policy behavior is understandable visually.
- [ ] Tests/mocks cover core behavior.
- [ ] Git milestone committed.

---

# Phase 8 — Terraform / Infrastructure as Code

**Status:** NOT STARTED

## Goal

Represent appropriate cloud infrastructure and IAM configuration as code.

## Scope

Use Terraform where it adds meaningful repeatability.

Do not convert every resource to Terraform just for volume.

## Dashboard Requirements

Create **Infrastructure** page displaying:

- Expected resources.
- Environment.
- IaC-managed resources.
- Deployment state.
- Drift/differences where feasible.

Terraform apply should not become an unsafe unrestricted UI button.

## Acceptance Criteria

- [ ] Terraform configuration validates.
- [ ] Secrets are externalized.
- [ ] Infrastructure is documented.
- [ ] Dashboard visualizes resulting state.
- [ ] Git milestone committed.

---

# Phase 9 — Docker & Operationalization

**Status:** NOT STARTED

## Goal

Package the supporting platform consistently.

## Deliverables

- Dockerfile.
- Container configuration.
- Health check.
- Startup documentation.
- Environment-variable handling.

## Dashboard Requirements

Create **System Health** page displaying:

- Application health.
- Database health.
- Entra connector health.
- Azure connector health.
- AWS connector health.
- System mode.
- Build/version.

## Acceptance Criteria

- [ ] Container builds.
- [ ] Container starts.
- [ ] Dashboard loads.
- [ ] Configuration remains externalized.
- [ ] Git milestone committed.

---

# Phase 10 — Unified IAM Command Center

**Status:** NOT STARTED

## Goal

Produce a polished, coherent demonstration of the complete platform.

## Navigation

1. Overview
2. Employees
3. JML Operations
4. Access Review
5. Security & Audit
6. Microsoft Entra
7. Azure
8. AWS
9. Infrastructure
10. System Health

## Overview Metrics

- Total employees.
- Active employees.
- Disabled employees.
- Joiners.
- Movers.
- Leavers.
- Privileged identities.
- Access violations.
- Stale permissions.
- MFA/security posture where available.
- Cloud connector state.
- Recent audit events.

## Final Acceptance Criteria

- [ ] Full demo flow works.
- [ ] Project is understandable without CLI-only interaction.
- [ ] All important IAM concepts are documented.
- [ ] Troubleshooting scenarios work.
- [ ] README is polished.
- [ ] Demo guide is complete.
- [ ] Interview notes are complete.
- [ ] Git history contains clear milestones.
- [ ] Final release tag created only after tests pass.

---

# Final Project Definition of Done

CILAMP is complete when the project owner can:

1. Demonstrate a Joiner.
2. Demonstrate a Mover.
3. Demonstrate a Leaver.
4. Explain RBAC.
5. Explain least privilege.
6. Detect excessive access.
7. Troubleshoot missing access.
8. Explain human vs workload identity.
9. Explain Entra ID integration.
10. Explain Azure RBAC.
11. Explain AWS IAM roles/policies.
12. Explain why managed identity is safer than hardcoded secrets.
13. Explain where PowerShell, Python, Terraform, and Docker fit.
14. Show audit history.
15. Explain the architecture confidently to faculty/recruiters/interviewers.
