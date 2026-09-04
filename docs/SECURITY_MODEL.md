# CILAMP — Security Model

## 1. Purpose

This document defines the security principles CILAMP must demonstrate and the controls that must govern development and cloud integration.

CILAMP is a learning/portfolio platform, but it should model responsible enterprise IAM behavior.

---

# 2. Core Security Principles

CILAMP must demonstrate:

1. Least privilege.
2. Role-Based Access Control.
3. Separation of duties.
4. Identity lifecycle management.
5. Strong authentication concepts.
6. Privilege creep prevention.
7. Access review.
8. Secure workload identity.
9. Auditing.
10. Secure credential handling.
11. Safe cloud experimentation.

---

# 3. Identity Types

## 3.1 Human Identities

Examples:

- Employee.
- Manager.
- IT administrator.
- Security administrator.

Human identities may receive:

- Department membership.
- Job-role access.
- Applications.
- Cloud roles.
- Privileged permissions.

Humans should use strong authentication and MFA where supported.

---

## 3.2 Workload Identities

Examples:

- Python automation.
- Background service.
- Cloud-hosted application.
- Deployment process.

Preferred authentication approaches:

- Azure Managed Identity.
- Entra Service Principal with safe credential strategy where necessary.
- AWS IAM Role / temporary credentials.
- Workload identity mechanisms.

Avoid long-lived static secrets.

---

# 4. Least Privilege

A user or workload should receive only the access required for its job.

Example:

Developer may need:

- GitHub.
- Jira.
- Development resources.
- Selected read/write permissions.

Developer should not automatically receive:

- Azure subscription Owner.
- AWS AdministratorAccess.
- IAM administration.
- HR data access.
- Finance administration.

The project must make excessive permissions visible.

---

# 5. RBAC Model

Access should primarily flow from:

```text
Employee
  ↓
Department + Job Role
  ↓
Groups
  ↓
Applications / Permissions
```

Direct user-specific grants should be minimized because they are harder to review and remove.

---

# 6. Joiner Security Rules

A Joiner workflow must:

- Validate employee record.
- Assign only access justified by role/department.
- Avoid privileged roles by default.
- Record every important access grant.
- Make resulting access visible for review.

---

# 7. Mover Security Rules

Mover is a high-risk lifecycle operation because old permissions can remain.

Rules:

1. Calculate current access.
2. Calculate desired new access.
3. Remove obsolete access.
4. Add new required access.
5. Validate resulting privileges.
6. Audit the full before/after change.

This protects against privilege creep.

---

# 8. Leaver Security Rules

Leaver workflow must:

- Disable identity.
- Revoke active access.
- Remove groups.
- Remove applications.
- Remove cloud authorization.
- Preserve historical audit evidence.
- Prevent accidental reactivation without deliberate action.

---

# 9. MFA and Conditional Access

The project should demonstrate the concepts of:

- MFA.
- Strong authentication.
- Conditional Access.
- Risk-aware authentication.

If live enforcement is unavailable because of lab licensing, the UI must clearly indicate that the feature is simulated/documented rather than live.

Never claim a live security control that is not actually active.

---

# 10. Privileged Access

Privileged identities require greater scrutiny.

Examples:

- IT Administrator.
- Security Administrator.
- Azure Owner.
- AWS account administration.
- IAM administration.

The project should:

- Identify privileged identities.
- Flag unexpected privileged assignments.
- Prefer temporary/elevated access concepts where applicable.
- Explain PIM/JIT concepts even if not available in the lab.

---

# 11. Secrets and Credentials

## Never Commit

- `.env`
- AWS access keys.
- AWS secret keys.
- Azure client secrets.
- Entra client secrets.
- Access tokens.
- Refresh tokens.
- Private keys.
- Database passwords for real environments.

## Allowed

`.env.example`

Example:

```text
ENTRA_TENANT_ID=your-lab-tenant-id
ENTRA_CLIENT_ID=your-lab-client-id
AWS_PROFILE=your-lab-profile
CILAMP_MODE=SIMULATION
```

No real secret values.

---

# 12. Cloud Credential Rules

## AWS

Never use:

- Root access keys.
- Root credentials in automation.

Prefer:

- AWS SSO / IAM Identity Center where available.
- Named local profile.
- IAM Role.
- Temporary credentials.

## Azure / Entra

Avoid broad privileges.

Prefer:

- Dedicated lab tenant/subscription.
- Least-privileged permissions.
- Managed identity when running in Azure.
- Appropriately scoped service principal only where needed.

Do not assume Global Administrator is required.

---

# 13. Simulation Safety

Simulation mode must never execute live cloud writes.

The current mode must be clearly visible in the UI.

Example:

```text
MODE: SIMULATION
```

Live lab mode:

```text
MODE: LIVE LAB
```

Significant live cloud writes should require explicit user confirmation.

---

## 13.1 Phase 0 Enforced Controls

The implemented foundation enforces these controls:

- `CILAMP_MODE` defaults to `SIMULATION`.
- Any attempt to start Phase 0 with `LIVE_LAB` is rejected before the dashboard can operate.
- `.env`, private keys, cloud credential files, Streamlit secrets, local databases, and Terraform state are excluded by `.gitignore`.
- `.env.example` contains placeholders and local non-secret settings only.
- No cloud SDK or connector is installed or invoked.
- Database health output reports operational state without displaying stored identity data or credentials.

These controls are verified by automated tests where practical.

## 13.2 Phase 1 Access Controls

- Employee identities are fictional, deterministic, and use the reserved `example.cilamp` domain.
- Every job role is compatible with exactly one business department in the current model.
- Effective access is derived from the authoritative role catalog rather than direct user grants.
- Normal business roles do not receive `cloud.ops.scoped` administration permission.
- Developer tests prove that Finance, HR, and scoped cloud-administration permissions are not granted.
- Privileged roles are explicitly marked for later access-review handling.
- Search query values are parameterized; the only dynamically selected distribution columns come from a fixed allowlist.

Phase 1 established expected access. Phase 3 now implements detection and remediation of actual-versus-expected differences.

## 13.3 Phase 2 Lifecycle Controls

- All JML writes remain local and require an explicit UI confirmation after preview.
- Joiner validates role compatibility, fictional email format, uniqueness, and active starting status.
- Mover calculates set differences from actual access to desired role access and revokes obsolete permissions before granting new permissions.
- Any excessive actual access not justified by the destination role appears in `to_remove` and is revoked, preventing privilege creep.
- Leaver disables the account and removes every actual group, application, and permission assignment while preserving the identity record.
- Execution occurs in one SQLite transaction and rejects stale previews whose underlying identity/access changed.
- Every security-relevant step records actor, target, action, old/new state, result, reason, timestamp, event ID, and correlation ID.
- Initialization never regrants access previously removed by a Leaver operation.

Phase 2 audit presentation is scoped to lifecycle operations. Cross-system security events, filters, troubleshooting, and the full Security & Audit Center belong to Phase 4.

## 13.4 Phase 3 Access Review Controls

- Expected access is calculated from identity status and the authoritative role catalog.
- Actual access is read independently from persisted group, application, and permission assignments.
- Disabled identities have an empty expected-access baseline.
- Unexpected privileged permissions/groups/applications are `CRITICAL`; other unauthorized or stale access is `HIGH`; missing required access is `MEDIUM`.
- `platform.administrator` is a simulation-only permission that no standard role receives.
- Creating the mandatory Developer→Administrator scenario requires explicit confirmation and produces an audit event.
- Remediation removes excess assignments and restores missing approved assignments without changing the employee's role.
- Remediation requires confirmation, executes transactionally, records correlated evidence, and rejects stale reviews.
- Access-source explanations distinguish role/group-policy access from direct or stale assignments.

Phase 3 does not claim that a local finding came from live Entra, Azure, or AWS state.

---

# 14. Logging Rules

Logs may include:

- Event ID.
- Timestamp.
- User identifier.
- Operation.
- Result.
- Error reason.
- Source module.

Logs must not include:

- Passwords.
- Tokens.
- Secret keys.
- Full sensitive credential payloads.

---

# 15. Audit Requirements

Important events include:

- User created.
- Role assigned.
- Group assigned.
- Application granted.
- Employee moved.
- Old access removed.
- New access granted.
- Employee disabled.
- Access revoked.
- Excess privilege detected.
- Privilege removed.
- Cloud connector operation failed.
- Cloud connector operation succeeded.

---

# 16. Security Findings

Security findings should include:

- Finding ID.
- Severity.
- Employee/workload.
- Expected access.
- Actual access.
- Reason.
- Recommended remediation.
- Status.

Suggested severities:

- LOW
- MEDIUM
- HIGH
- CRITICAL

---

# 17. Threat Scenarios to Demonstrate

## Scenario 1 — Excess Privilege

Developer receives administrator permission.

Expected:

- Finding generated.
- Risk displayed.
- Remediation suggested.

## Scenario 2 — Privilege Creep

Employee moves Engineering → Finance but keeps Engineering access.

Expected:

- Stale access detected.
- Old permission identified.
- Remediation available.

## Scenario 3 — Incomplete Offboarding

Disabled employee still has application access.

Expected:

- Critical finding.
- Remaining access listed.

## Scenario 4 — Unauthorized Group Membership

Finance employee manually appears in Security Admin group.

Expected:

- Unexpected group membership flagged.

## Scenario 5 — Workload Secret Anti-Pattern

Simulation indicates an application is configured with a static secret.

Expected:

- Risk explanation.
- Recommended managed identity / IAM role design.

## Scenario 6 — Missing Access

Employee should access CRM but cannot.

Expected troubleshooting:

- Account state.
- Group membership.
- Role.
- Application assignment.
- MFA/Conditional Access concept.
- Cloud authorization.
- Logs.

---

# 18. Security Definition of Done

No phase involving cloud/security is complete unless:

- [ ] Secrets are externalized.
- [ ] Least privilege is considered.
- [ ] Access changes are auditable.
- [ ] Live vs simulation state is clear.
- [ ] Security failures are represented honestly.
- [ ] Relevant security tests pass.
- [ ] Documentation explains the security rationale.
