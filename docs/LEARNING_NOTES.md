# CILAMP — Learning Notes

> **Audience:** Project owner.
> **Purpose:** Explain the IAM/cloud concepts implemented in CILAMP in simple language so they can be demonstrated and discussed in interviews.

Claude/Codex should update this file whenever an important new IAM/cloud concept is implemented.

---

# How to Use This File

For every major concept, maintain:

1. What it is.
2. Why companies use it.
3. Where it exists in CILAMP.
4. How to demonstrate it.
5. Common problems.
6. Troubleshooting.
7. Interview explanation.

---

# 1. Identity and Access Management (IAM)

## What It Is

IAM answers two major questions:

1. **Who are you?**
2. **What are you allowed to access?**

In an organization, IAM manages employees, administrators, applications, cloud workloads, roles, groups, and permissions.

## Why Companies Use It

Without IAM:

- Anyone could receive excessive access.
- Former employees may retain access.
- Security teams may not know who has access to sensitive systems.
- Auditing becomes difficult.

## Where CILAMP Uses It

The entire project is an IAM platform.

CILAMP models:

- Employees.
- Departments.
- Roles.
- Groups.
- Applications.
- Permissions.
- Lifecycle events.
- Cloud identities.

## Interview Explanation

> CILAMP models enterprise identity lifecycle management. It determines what access a user should receive based on department and job role, manages that access through the Joiner-Mover-Leaver lifecycle, and audits changes.

---

# 2. Authentication vs Authorization

## Authentication

**Authentication = proving who you are.**

Example:

- Password.
- MFA.
- Security key.

## Authorization

**Authorization = determining what you are allowed to do.**

Example:

A user may successfully sign in to Azure but still not have permission to read a particular storage account.

## Interview Explanation

> Authentication verifies the identity. Authorization determines the permissions of that authenticated identity.

---

# 3. Joiner-Mover-Leaver (JML)

## Joiner

Employee joins the company.

Typical actions:

- Create identity.
- Assign groups.
- Assign role.
- Assign applications.
- Apply security controls.

## Mover

Employee changes role or department.

Most important security requirement:

**Remove obsolete access.**

Otherwise privilege creep occurs.

## Leaver

Employee leaves.

Typical actions:

- Disable identity.
- Revoke applications.
- Remove groups.
- Remove cloud access.
- Preserve audit history.

## Why It Matters

JML ensures access follows the employee's actual job requirements.

## Interview Explanation

> I designed CILAMP around the Joiner-Mover-Leaver lifecycle. Joiners receive role-appropriate access, movers lose obsolete access before receiving new permissions, and leavers are disabled and have access revoked.

---

# 4. Role-Based Access Control (RBAC)

## What It Is

RBAC assigns permissions based on roles rather than manually granting permissions to every individual.

Example:

```text
Rahul
  ↓
Developer Role
  ↓
GitHub + Jira + Development Access
```

## Why Companies Use It

It improves:

- Consistency.
- Scalability.
- Auditing.
- Access reviews.

## CILAMP Usage

CILAMP maps:

```text
Department + Job Role
        ↓
Groups
        ↓
Applications
        ↓
Permissions
```

## Interview Explanation

> I used RBAC so permissions are determined by business roles instead of arbitrary user-specific grants.

---

# 5. Least Privilege

## What It Is

Give each person or workload only the permissions required for the task.

## Example

Developer:

Allowed:

- Read development logs.
- Work with development resources.

Not automatically allowed:

- Production Owner.
- IAM administrator.
- Finance administrator.

## CILAMP Demonstration

CILAMP will deliberately assign excessive access to an employee and detect the violation.

## Interview Explanation

> I implemented least-privilege validation by comparing expected access from the employee's business role against actual assigned access.

---

# 6. Privilege Creep

## What It Is

An employee accumulates old permissions over time.

Example:

```text
Engineering Developer
        ↓ moves to
Finance Analyst
```

If Engineering permissions remain, the employee has more access than required.

## CILAMP Prevention

Mover workflow:

1. Determine old access.
2. Determine desired new access.
3. Remove obsolete access.
4. Add new access.
5. Validate final state.

---

# 7. Groups

## What They Are

Groups collect users so access can be managed as a set.

Example:

```text
Engineering-Developers Group
        ↓
GitHub
Jira
Development resources
```

Instead of assigning all permissions individually to Rahul, Rahul becomes a member of the group.

---

# 8. MFA

## What It Is

Multi-Factor Authentication requires more than one proof of identity.

Typical example:

- Password.
- Authentication app.

## Why It Matters

A stolen password alone should not automatically allow account takeover.

## CILAMP

MFA/security posture may initially be simulated and later represented using Entra capabilities depending on lab licensing.

---

# 9. Microsoft Entra ID

## What It Is

Microsoft's cloud identity platform.

It manages:

- Users.
- Groups.
- Authentication.
- Applications.
- Service principals.
- Identity/security policies.

## CILAMP Usage

Later phases will integrate the local identity model with a safe Entra lab.

---

# 10. Azure RBAC

## What It Is

Azure RBAC controls who can perform which actions on Azure resources and at what scope.

Possible scopes include:

- Subscription.
- Resource group.
- Individual resource.

## Example

Developer may receive read access to a development storage account without receiving Owner access to the entire subscription.

## Interview Explanation

> I used Azure RBAC to demonstrate scoped least-privilege access rather than broad subscription-level permissions.

---

# 11. AWS IAM

## What It Is

AWS IAM controls identities and permissions in AWS.

Major concepts:

- IAM users.
- IAM roles.
- Policies.
- Permission evaluation.
- Temporary credentials.
- Resource access.

## CILAMP

The AWS phase will demonstrate a role with only the permissions required for selected resources.

---

# 12. IAM Role vs IAM Policy in AWS

## Role

An identity that can be assumed.

## Policy

A document describing allowed or denied actions.

Example:

```text
Developer Role
     ↓
Policy
     ↓
Allow selected S3 read
```

---

# 13. Human Identity vs Workload Identity

## Human Identity

Used by a person.

Examples:

- Employee.
- Administrator.

## Workload Identity

Used by software or automation.

Examples:

- Application.
- Script.
- Cloud service.

Workloads should avoid storing long-lived passwords/secrets.

---

# 14. Service Principal

## What It Is

An identity representing an application/service in Microsoft Entra.

It allows software to authenticate and receive authorization.

## Important

A service principal does not automatically mean credentials are safely handled. Authentication method still matters.

---

# 15. Managed Identity

## What It Is

A managed identity is an Azure-managed identity for a supported Azure resource.

The platform manages the underlying credentials.

## Why It Is Useful

Instead of:

```text
Application
  ↓
Hardcoded secret
```

Use:

```text
Application
  ↓
Managed Identity
  ↓
Azure RBAC
  ↓
Resource
```

## Interview Explanation

> I demonstrated managed identity to remove the need to embed long-lived cloud credentials in application code.

---

# 16. Microsoft Graph

## What It Is

Microsoft Graph provides APIs for interacting with Microsoft cloud services including Entra identities.

## CILAMP Usage

The Entra connector may use Graph to:

- Read users.
- Read groups.
- Manage selected lab group memberships.
- Inspect application identities.

---

# 17. PowerShell

## Why It Exists in CILAMP

PowerShell is widely used for Microsoft administration and repetitive identity tasks.

Examples:

- User operations.
- Group membership.
- Reporting.
- Administration.

The project owner does not need to become a PowerShell developer, but should understand what each script changes and how to validate it.

---

# 18. Python

## Why It Exists in CILAMP

Python implements:

- Local simulation.
- JML orchestration.
- Policy evaluation.
- Audit logic.
- Dashboard support.
- Cloud API integration.

Python supports the IAM platform; Python development is not the main portfolio story.

---

# 19. Terraform

## What It Is

Terraform is Infrastructure as Code.

It allows infrastructure and IAM-related resources to be defined in version-controlled configuration.

## Why It Matters

Benefits:

- Repeatability.
- Consistency.
- Reviewable changes.
- Reduced manual configuration.

---

# 20. Docker

## What It Is

Docker packages the application and its dependencies into a container image.

## Why CILAMP Uses It

It demonstrates how the supporting IAM platform can be packaged and run consistently.

Docker is not the main purpose of the project.

---

# 21. Audit Logging

## Why It Matters

Organizations need to answer:

- Who changed access?
- What changed?
- When?
- Was it successful?
- What was the previous state?

CILAMP records identity lifecycle and security events.

---

# 22. Troubleshooting IAM Access

A useful generic approach:

```text
Does identity exist?
      ↓
Is account enabled?
      ↓
Authentication successful?
      ↓
Correct department/role?
      ↓
Correct group?
      ↓
Correct application assignment?
      ↓
Correct cloud role/policy?
      ↓
Security policy blocking?
      ↓
Check logs/audit
```

This is more valuable for a Cloud/IAM role than memorizing code.

---

# 23. Phase 0 — Simulation Safety and Health Checks

## What It Is

Phase 0 establishes a safe control plane for future IAM work. It provides a visible operating mode, an initialized local data store, module status, and health signals without connecting to a cloud.

## Why Enterprises Use It

Operators need to know which environment they are using and whether dependencies are healthy before performing identity changes. Clear environment boundaries reduce the chance of a test action reaching production.

## Where It Is Implemented

- `src/cilamp/config.py` allows `SIMULATION` only.
- `src/cilamp/database.py` initializes SQLite idempotently and checks health.
- `dashboard/app.py` displays mode, phase, database state, and disconnected cloud integrations.
- `.gitignore` and `.env.example` establish secure configuration handling.

## How to Demonstrate It Manually

1. Start the dashboard.
2. Point out the green `SIMULATION` badge.
3. Show application and SQLite health.
4. Show that employee count is zero because organization data belongs to Phase 1.
5. Show Entra ID, Azure, and AWS as not connected.

## Safe Failure Scenario

Set `CILAMP_MODE=LIVE_LAB` and start the dashboard. Phase 0 should stop with a clear validation error because live integration has not been approved or implemented. Return the value to `SIMULATION` afterward.

## Troubleshooting

If the database is unhealthy, verify the configured path and write permissions. If the dashboard cannot import `cilamp`, install the project with `python -m pip install -e ".[dev]"` from the repository root.

## Interview Explanation

> I started with a simulation-only control center that makes environment and dependency health explicit. The application fails closed if live-lab mode is requested before cloud connectors and confirmation controls exist, which is a practical guardrail against accidental cloud changes.

---

# 24. Phase 1 — Organization Model and Access Matrix

## What It Is

The organization model connects business facts—department and job role—to expected identity access. The access matrix shows the complete path from role to groups, applications, and permissions.

## Why Enterprises Use It

Without an authoritative model, administrators grant access case by case, creating inconsistency and privilege creep. A role catalog makes onboarding predictable and gives access reviewers a baseline for deciding whether access is justified.

## Where It Is Implemented

- `src/cilamp/domain.py`: identity and access objects.
- `src/cilamp/iam_catalog.py`: departments, roles, groups, applications, permissions, and mappings.
- `src/cilamp/organization.py`: deterministic 500-employee HR-source simulation.
- `src/cilamp/repository.py`: idempotent persistence, queries, and effective-access lookup.
- `dashboard/app.py`: Organization Explorer, profiles, distributions, and Access Matrix.

## How to Demonstrate It Manually

1. Open Overview and show 500 employees across six departments and ten roles.
2. Open Organization Explorer and filter Engineering → Developer.
3. Open an employee profile and trace their role-derived groups, applications, and permissions.
4. Open Access Matrix and compare Developer with Finance Manager or IT Administrator.
5. Point out that access to an application does not automatically equal administrative permission.

## Safe Failure Scenario

Search for a nonexistent employee or choose a department/role combination with no matching identity. The UI should show zero matches without changing data. For a policy check, inspect the Developer row and verify it has no Finance or HR permission.

## Troubleshooting

If counts are missing, check SQLite health and rerun the application so idempotent initialization completes. If access looks wrong, first inspect the employee's department and job role, then compare the role entry in `iam_catalog.py`; do not patch individual users to hide a catalog error.

## Interview Explanation

> I modeled a fictional 500-employee enterprise with department-compatible job roles. A single authoritative catalog maps each role to groups, applications, and least-privilege permissions. The Streamlit explorer makes effective access understandable, while deterministic data and automated tests keep the access baseline reproducible.

---

# 25. Phase 2 — Implemented Joiner-Mover-Leaver Operations

## What It Is

Joiner-Mover-Leaver is the operational lifecycle for creating an identity, changing justified access as the employee's business role changes, and disabling the identity when employment ends.

## Why Enterprises Use It

Identity risk often comes from delayed onboarding, incorrect manual grants, retained access after transfers, and incomplete offboarding. A controlled JML process makes access consistent and auditable throughout employment.

## Where It Is Implemented

- `src/cilamp/lifecycle.py`: pure transition planning and access differences.
- `src/cilamp/lifecycle_service.py`: validation and orchestration.
- `src/cilamp/repository.py`: actual assignments, transactions, stale-preview checks, and correlated audit events.
- `dashboard/app.py`: Joiner, Mover, Leaver, confirmation, result, and audit timeline UI.

## How to Demonstrate It Manually

1. Create a fictional Developer through Joiner and inspect granted access and audit actions.
2. Move that identity to Finance Analyst and explain the access-to-remove and access-to-add preview.
3. Confirm the Mover and verify Engineering/GitHub access disappeared before Finance access was granted.
4. Preview Leaver and show every assignment that will be revoked.
5. Confirm Leaver, then show `DISABLED`, empty access, and the correlation-linked audit timeline.

## Safe Failure Scenario

Preview moving an employee to the role they already hold. The system rejects the no-op. Another safe scenario is previewing an operation, changing the same identity through a separate operation, then attempting the old plan; stale-state validation rejects it.

## Troubleshooting

Start with the correlation ID. Check the plan's before state, removal set, addition set, employee status, and ordered audit actions. For a Mover, verify obsolete permissions were revoked before any permission grant. For a Leaver, verify both disabled status and empty assignment tables; either condition alone is incomplete offboarding.

## Interview Explanation

> I implemented provider-independent JML workflows with an explicit preview and confirmation boundary. Joiners receive only role-derived access, Movers remove obsolete and excessive access before adding the destination role, and Leavers are disabled with all assignments revoked. Each operation is transactional in simulation mode and produces correlated audit events for traceability.

---

# 26. Phase 3 — Expected vs Actual Access Review

## What It Is

An access review compares what an identity should have according to business policy with what it actually has. Differences may be excessive privilege, unauthorized assignments, stale access from an old role, or missing access needed for work.

## Why Enterprises Use It

Provisioning processes are not perfect. Manual changes, incomplete transfers, exceptions, and configuration mistakes can cause actual access to drift away from policy. Regular review detects that drift and provides evidence for remediation.

## Where It Is Implemented

- `src/cilamp/policy.py`: expected access, findings, risk, privileged identities, and access-source explanations.
- `src/cilamp/access_review_service.py`: organization review, mandatory scenario, summaries, and remediation coordination.
- `src/cilamp/repository.py`: controlled scenario grant, transactional reconciliation, concurrency checks, and audit evidence.
- `dashboard/app.py`: Access Review Center, filters, expected/actual/difference/source views, and remediation controls.

## How to Demonstrate It Manually

1. Open Access Review and show that the clean organization is compliant.
2. Expand the scenario panel, select a Developer, confirm, and grant the simulated Administrator permission.
3. Inspect the identity: expected access excludes `platform.administrator`, actual access includes it, and the finding is `CRITICAL` excessive privilege.
4. Explain the source as a direct/stale assignment outside role policy.
5. Confirm remediation and show that the identity returns to compliant state.
6. Open the lifecycle audit timeline to locate the scenario and remediation correlation IDs.

## Safe Failure Scenario

Create the Administrator scenario twice for the same Developer; the duplicate grant is rejected. Another safe test is to review an identity, change its assignments, and then attempt the old remediation; the stale review is rejected.

## Troubleshooting

Verify identity status and role first, then compare expected and actual groups, applications, and permissions. Determine whether a difference is excess or missing. Follow the correlation ID for scenario/remediation evidence. Do not resolve an access problem by granting broad Administrator access.

## Interview Explanation

> I built an access-review engine that compares role-based expected access with actual persisted assignments. It risk-rates excessive, unauthorized, stale, and missing access, identifies privileged identities, explains assignment sources, and supports confirmed transactional remediation with audit evidence. A deliberate Developer-to-Administrator scenario demonstrates least-privilege violation detection.

---

# 27. Phase 4 — Security Findings, Audit Evidence, and Troubleshooting

## What It Is

An audit event records something that happened; a security finding records a problem that needs investigation; an access review calculates whether current assignments match policy. They are related but serve different purposes.

## Why Enterprises Use It

Security and IAM teams must reconstruct who changed access, identify failed controls, prioritize risks, investigate an identity over time, and prove how a problem was resolved. Keeping history separate from case status prevents evidence from being overwritten.

## Where It Is Implemented

- `src/cilamp/security.py`: six scenario plans and scenario-specific troubleshooting steps.
- `src/cilamp/security_service.py`: eligible targets, previews, case creation, and remediation coordination.
- `src/cilamp/repository.py`: security findings, failed/successful audit events, filters, and resolution evidence.
- `dashboard/app.py`: Scenario Lab, Security Findings, Audit Events, Identity Timeline, Privileged Activity, and Troubleshooting tabs.

## How to Demonstrate It Manually

1. Open Security & Audit and choose one scenario in Scenario Lab.
2. Preview its exact simulated state change and evidence, then confirm creation.
3. Show the new `OPEN` finding and the failed control-check event.
4. Filter Audit Events by `FAILURE` and follow the correlation ID.
5. Open Identity Timeline and Privileged Activity where relevant.
6. Use Troubleshooting to explain the checks, confirm remediation, and show the case becomes `REMEDIATED` while historical failure evidence remains.

## Safe Failure Scenario

Attempt to create the same open scenario for the same target twice. The duplicate is rejected. The intentionally failed control check remains a truthful `FAILURE`; it is not converted to success after remediation.

## Troubleshooting

Start from the finding, verify evidence and current identity state, then follow its correlation ID through audit events. Separate the failed security control from the successfully executed simulation action. Reconcile human access to policy or, for workload credentials, document the managed/federated identity resolution without storing a secret.

## Interview Explanation

> I built a Security & Audit Center that separates append-only audit evidence, current-state RBAC evaluation, and mutable security-case status. Six IAM scenarios create risk-rated findings and truthful failed control events. Analysts can filter events, inspect identity timelines and privileged activity, follow guided troubleshooting, and perform confirmed remediation with correlated evidence.

---

# Concepts Still To Be Added

Claude/Codex should add detailed notes as these are implemented:

- [ ] Conditional Access.
- [ ] PIM.
- [ ] Access reviews.
- [ ] STS.
- [ ] AWS policy evaluation.
- [ ] Key Vault.
- [ ] CloudTrail.
- [ ] Azure Monitor.
- [ ] Workload identity federation.
- [ ] Terraform state.
- [ ] Docker health checks.
# Phase 5 Learning Note — Microsoft Entra Connector and Safe Lab Operations

## What it is

Microsoft Entra ID is Microsoft's cloud identity directory. Microsoft Graph is the API surface used here to read directory objects and, when separately authorized, perform narrow lab changes. CILAMP represents human identities as users and application/workload identities as service principals.

## Why enterprises use it

Enterprises centralize authentication identities, group-based authorization, application identities, and directory audit evidence in Entra. Automation reduces manual assignment mistakes, but it must operate with limited permissions, clear change control, and reliable evidence.

## Where it is implemented

- `src/cilamp/connectors/entra/base.py`: provider contract.
- `src/cilamp/connectors/entra/simulation.py`: offline Entra-shaped directory.
- `src/cilamp/connectors/entra/graph.py`: Microsoft Graph v1.0 and Azure Identity adapter.
- `src/cilamp/entra_service.py`: safety and orchestration boundary.
- `src/cilamp/entra_repository.py`: synchronized cache and operation evidence.
- `dashboard/app.py`: Microsoft Entra visual control center.

## How to demonstrate it manually

1. Start in `SIMULATION` and open **Microsoft Entra**.
2. Select **Synchronize Entra Directory** and verify 500 users, 13 groups, and 10 application identities.
3. Open **Groups & Memberships**, select a group, and refresh its members.
4. Compare a human user with a service principal in **Application Identities**.
5. In **Lab Readiness & Writes**, confirm a simulated profile or membership update.
6. Verify the result and correlation ID in **Entra Operations**.

For a real dedicated lab, configure the non-secret controls from `.env.example`, authenticate to the correct tenant with Azure CLI, start in read-only mode, and synchronize. Do not enable writes until the UPN suffix, group allowlist, consent, and operator role are reviewed.

## Common troubleshooting

- Authentication failure: confirm `az account show`, tenant selection, token availability, and local clock.
- HTTP 403: identify the exact endpoint and compare consent plus the signed-in operator's Entra role; do not add broad permissions blindly.
- Empty results: verify the target tenant, object type, and Graph pagination rather than assuming the directory is empty.
- Audit tab unavailable: check `AuditLog.Read.All`, Reports/Security Reader-type role requirements, retention, and licensing.
- Write blocked locally: check mode, lab guard, write switch, UPN suffix, group allowlist, synchronized target, and UI confirmation.
- Graph write succeeds but the next read looks stale: account for directory replication delay and synchronize again.

## What you should personally understand

- Authentication proves which identity calls Graph; authorization decides which Graph operation it may perform.
- Delegated/application permissions and Entra directory roles are related but different controls.
- A service principal represents an application in a tenant; it is not the application's secret.
- `User.Read.All` does not authorize user updates, and read permissions should not be expanded merely to make a demo convenient.
- A local cache is a timestamped projection, not proof of current directory state.
- Mocked connector tests prove request construction and safety behavior, not that a real tenant granted consent or completed an operation.

## Interview explanation

“I integrated Microsoft Entra through a provider interface so the JML and RBAC logic remains cloud-independent. The default adapter is a deterministic simulation; the live adapter uses Azure Identity and Microsoft Graph against an explicitly selected lab tenant. Reads cache users, groups, memberships, service principals, and optional audit data for the dashboard. Live writes are disabled by default and constrained by confirmation, allowed UPN domain, and group allowlist. Provider failures remain truthful audit records, and no passwords, client secrets, or tokens are persisted.”

---

# Phase 6 Learning Note — Azure RBAC and Managed Identity

## What it is

Azure RBAC controls which security principal can perform which actions at which Azure scope. A role assignment joins three things: a user/group/service principal/managed identity, a role definition, and a scope such as subscription, resource group, or individual resource.

## Why enterprises use it

Enterprises use Azure RBAC to avoid shared administrator credentials and limit the blast radius of compromise. Scope lets the same role be powerful only where it is needed. Data-plane roles protect data operations separately from management-plane resource configuration.

## Where it is implemented

- `src/cilamp/connectors/azure/simulation.py`: deterministic resource/RBAC lab.
- `src/cilamp/connectors/azure/arm.py`: tenant-checked, read-only ARM discovery.
- `src/cilamp/azure_policy.py`: scope and action evaluation.
- `src/cilamp/azure_repository.py`: timestamped Azure cache and operation evidence.
- `src/cilamp/azure_service.py`: simulation/live routing and failure recording.
- `dashboard/app.py`: Azure Access visual control center.

## How to demonstrate it manually

1. Open **Azure Access** in `SIMULATION` mode and select **Synchronize Azure RBAC**.
2. Show the resource group, two storage accounts, Key Vault, and application resource.
3. Show that the Developers group has `Storage Blob Data Reader` only on `stcilampdev`.
4. Prove blob read is allowed while blob write, archive storage read, and RBAC administration are not granted.
5. Select `reporting-api-mi` and show Key Vault secret read allowed but role-assignment management not granted.
6. Compare the bad hardcoded-secret diagram with the managed-identity path.
7. Show the synchronization result and correlation ID under **Azure Operations**.

## What you should personally understand

- Azure RBAC answers “who, can do what, at which scope.”
- A role definition lists permitted actions; a role assignment attaches it to a principal and scope.
- Parent-scope permissions can be inherited by child resources, so narrow scopes reduce blast radius.
- Azure `Reader` is management-plane visibility and does not automatically allow reading blob content or Key Vault secret values.
- A managed identity is a workload identity whose credentials are managed by Azure. It still needs RBAC authorization.
- No matching allow is “not granted”; an explicit deny assignment is a separate Azure object.
- Custom roles, conditions, deny assignments, or unresolved groups require more provider evidence, so `UNKNOWN` is the honest result.

## Common troubleshooting

- HTTP 403 during sync: verify read access at the configured resource group and permission to read role assignments; do not default to Owner.
- Wrong tenant: verify Azure CLI context, configured tenant/subscription, and the token tenant claim.
- Empty inventory: verify exact resource-group spelling and subscription context.
- Blob access missing despite Reader: use a narrowly scoped data-plane role such as Storage Blob Data Reader.
- Managed identity access failure: match the principal ID, role, scope, token audience, and propagation state.
- `UNKNOWN`: inspect custom-role actions, conditions, deny assignments, and group expansion directly in Azure.

## Interview explanation

“I modeled Azure RBAC as a security principal, role definition, and scope rather than merely listing role names. The simulation demonstrates inheritance, narrow resource access, management/data-plane separation, and managed identities replacing application secrets. The optional live adapter performs tenant-verified, resource-group-scoped ARM reads only. The evaluator reports allowed, not granted, or unknown so custom roles and conditions are not misrepresented.”

---
