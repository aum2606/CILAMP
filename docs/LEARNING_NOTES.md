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
