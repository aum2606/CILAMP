# CILAMP — Demo Guide

## Purpose

This document explains how to demonstrate CILAMP to:

- Faculty.
- Recruiters.
- Cloud/IAM interviewers.

The demo should focus on the business problem and security value rather than code.

---

# 1. 30-Second Introduction

> CILAMP is a Cloud Identity Lifecycle & Access Management Platform designed for a simulated 500-employee organization. It manages employee access through the Joiner-Mover-Leaver lifecycle, applies RBAC and least privilege, identifies excessive or stale access, maintains audit history, and later integrates with Microsoft Entra ID, Azure, and AWS IAM.

---

# 2. Simple Faculty Explanation

> Imagine a company with 500 employees. Different employees need different applications and cloud permissions. When someone joins, changes department, or leaves, the IT team must ensure the correct access is granted or removed. CILAMP automates and visualizes that identity lifecycle while applying security principles such as role-based access, least privilege, MFA concepts, and auditing.

---

# 3. Recommended Demo Order

## Phase 0 Foundation Demo

Use this section when explaining the original Phase 0 foundation:

1. Start the dashboard and identify the `SIMULATION` mode badge.
2. Show `Phase 0 — Foundation` and explain that no cloud writes are possible.
3. Show healthy application and SQLite status.
4. Show zero employees and explain that the organization model intentionally belongs to Phase 1.
5. Show every future IAM capability as not started/not connected.

Then continue to the implemented Phase 1–3 demonstrations below.

## Phase 1 Organization Demo

Phase 1 is now available:

1. On Overview, show the 500-employee count and department/role distributions.
2. Open Organization Explorer and search by name, employee ID, or fictional email.
3. Filter by department and role; use Engineering → Developer as the clearest example.
4. Open a profile and explain that access is inherited from the approved job role.
5. Open Access Matrix and trace role → groups → applications → permissions.
6. Compare Developer and IT Administrator to demonstrate least privilege and privileged-role identification.

Be explicit that the data is simulated and that Entra ID, Azure, and AWS remain disconnected.

## Phase 2 JML Demo

Phase 2 is now available in **JML Operations**:

1. **Joiner:** enter fictional information, select a department-compatible role, preview all grants, confirm, and show the resulting identity and audit actions.
2. **Mover:** select an active identity, choose a new department/role, and pause on the preview. Explain why obsolete access is removed before new access is granted. Confirm and show the final profile.
3. **Leaver:** select an active identity, preview every revocation, confirm, and show the disabled account with empty groups, applications, and permissions.
4. **Audit Timeline:** identify one operation by its correlation ID and show its ordered security-relevant actions.

Recommended narrative:

> The business role defines expected access. The lifecycle engine calculates the difference from actual access, requires confirmation, applies the safe transition, and records evidence. Everything shown is local simulation; no cloud directory or resource is modified.

## Phase 3 Access Review Demo

1. Open **Access Review** and show the clean compliance, findings, critical, and privileged-identity metrics.
2. Expand **Create mandatory excessive-privilege scenario**.
3. Select a Developer, confirm, and grant the simulated `platform.administrator` permission.
4. Inspect Expected Access, Actual Access, Differences, and Access Sources.
5. Highlight `CRITICAL`, `EXCESSIVE_PRIVILEGE`, the explanation, and suggested remediation.
6. Confirm **Remediate to Role Baseline**.
7. Show the identity is compliant and correlate the operation in the audit timeline.

Explain:

> The review engine does not trust job title alone. It compares policy with actual assignments. The Developer's Administrator permission is outside the approved baseline, so it is flagged as critical and removed through an audited remediation.

## Phase 4 Security & Audit Demo

1. Open **Security & Audit** and show audit, failure, open, and remediated metrics.
2. In Scenario Lab, explain the six available IAM/security cases.
3. Create one scenario after preview and confirmation. The missing-application or disabled-with-access cases are strong troubleshooting demonstrations.
4. In Security Findings, filter by risk/status/scenario and locate the new case.
5. In Audit Events, filter `Result = FAILURE`; explain that the control check failed truthfully while scenario creation succeeded.
6. Use Identity Timeline to reconstruct the target's history.
7. Use Privileged Activity for an Administrator scenario.
8. Open Troubleshooting, work through the checklist, confirm remediation, and show the finding closed without deleting the original failure event.

For the workload scenario, explicitly show `secret_value_stored: NO` and explain the recommended managed/federated identity pattern.

## Demo 1 — Overview

Show:

- Employee count.
- Departments.
- Active/disabled users.
- Current project mode.
- Security status.

Explain:

> This dashboard represents the identity environment of the fictional organization.

---

## Demo 2 — Employee Profile

Open a developer.

Show:

- Department.
- Role.
- Groups.
- Applications.
- Permissions.
- Status.

Explain:

> Access is derived from business role rather than randomly assigned per user.

---

## Demo 3 — Joiner

Create a fictional Engineering Developer.

Before submission explain:

> The system should determine access from role and department.

After onboarding show:

- Engineering group.
- Developer role.
- GitHub/Jira.
- Development access.
- Audit event.

Explain:

> This reduces manual provisioning errors.

---

## Demo 4 — Mover

Move employee:

```text
Engineering → Finance
```

Show before/after.

Highlight:

**Access removed**

- Engineering.
- Developer.
- GitHub.
- Development resource permissions.

**Access added**

- Finance.
- Finance Analyst.
- Finance application.

Explain:

> The important part is removing old access to prevent privilege creep.

---

## Demo 5 — Excess Privilege

Create or select scenario:

Developer has Administrator permission.

Show finding:

- Expected access.
- Actual access.
- Excess permission.
- Risk.
- Recommended remediation.

Explain:

> The platform compares actual access against expected role-based access and identifies violations.

---

## Demo 6 — Leaver

Select employee.

Show all access to be revoked.

Confirm offboarding.

Show:

- Account disabled.
- Groups removed.
- Applications removed.
- Permissions revoked.
- Audit event.

Explain:

> Former employees should not retain access after termination.

---

## Demo 7 — Audit

Open Security & Audit Center.

Show lifecycle timeline.

Explain:

> Every important access change is recorded so the organization can investigate who changed what and when.

---

# 4. Cloud Integration Demo

Only demonstrate live cloud functionality once implemented and stable.

## Entra

Show:

- Lab connection.
- Users/groups.
- Selected synchronized identities.

Explain:

> The local lifecycle logic can be translated into real Entra identity operations through Microsoft Graph.

## Azure

Show:

- Resource.
- Identity.
- Role.
- Scope.

Explain:

> Azure RBAC controls what an identity can do and where.

## AWS

Show:

- IAM role.
- Policy.
- Allowed resource operations.
- Not-granted admin actions.

Explain:

> The same least-privilege principle applies across clouds even though each provider uses different IAM constructs.

---

# 5. Workload Identity Demo

Show comparison:

## Insecure Pattern

```text
Application
   ↓
Hardcoded Secret
   ↓
Cloud
```

## Better Pattern

```text
Application
   ↓
Managed Identity / IAM Role
   ↓
RBAC / IAM Policy
   ↓
Cloud Resource
```

Explain:

> Workloads should receive identities and temporary/platform-managed credentials rather than storing passwords in source code.

---

# 6. What NOT to Do During Demo

Do not:

- Open dozens of source-code files first.
- Explain Python internals unless asked.
- Claim simulated features are live.
- Expose tenant IDs, credentials, or sensitive configuration unnecessarily.
- Spend the demo discussing Streamlit styling.
- Describe the project as a CRUD application.

---

# 7. Faculty Q&A

## Q: What problem does this solve?

> It reduces manual identity-management errors and helps ensure employees receive the correct access throughout their employment lifecycle.

## Q: Why 500 employees?

> It represents a realistic mid-sized organization where manual access management becomes difficult to scale.

## Q: Why not just use Entra ID directly?

> Entra ID is one of the real identity platforms used later. CILAMP first models the business logic and security policy, then integrates those rules with cloud providers. The project is demonstrating the full lifecycle, automation, policy validation, and multi-cloud view.

## Q: Is this a software development project?

> Software is used to implement and visualize the solution, but the primary focus is cloud identity, authorization, lifecycle management, automation, security, and troubleshooting.

## Q: Why use AWS too?

> It demonstrates that IAM and least-privilege principles apply across multiple cloud providers.

## Q: What is the most important part?

> Joiner-Mover-Leaver lifecycle management and preventing incorrect or excessive access.

---

# 8. Interview Version

> I designed a cloud identity lifecycle platform for a simulated 500-employee enterprise. Access is driven by department and job role. The Joiner workflow provisions required access, the Mover workflow removes obsolete permissions before adding new ones, and the Leaver workflow disables the identity and revokes access. I added an access-review engine to detect privilege creep and excessive permissions, maintained audit history, and extended the design to Microsoft Entra ID, Azure RBAC, AWS IAM, and workload identities. PowerShell, Python, Terraform, and Docker are used as supporting automation and operational tools.

---

# 9. Demo Checklist

Before presenting:

- [ ] Git working tree clean.
- [ ] Correct project mode displayed.
- [ ] Dashboard launches.
- [ ] Database healthy.
- [ ] Sample employees available.
- [ ] Joiner scenario works.
- [ ] Mover scenario works.
- [ ] Leaver scenario works.
- [ ] Excess privilege scenario works.
- [ ] Audit events visible.
- [ ] No secrets shown.
- [ ] Live cloud connectors healthy if being demonstrated.
- [ ] Fallback simulation available.
# Phase 5 — Microsoft Entra Lab Demo

1. Launch the dashboard in the default `SIMULATION` mode and open **Microsoft Entra**.
2. Point out connection status, mode, safe tenant label, and last synchronization.
3. Synchronize and show users, groups, service principals, and the simulated directory audit record.
4. Refresh a selected group's membership and explain that group-based authorization scales better than direct grants.
5. Open **Lab Readiness & Writes** and show the separate read/write permissions.
6. Confirm one simulated profile update or membership change, then find its correlation ID under **Entra Operations**.
7. Explain that live mode uses the same service contract but additionally requires the dedicated-tenant guard, external Azure authentication, a write switch, a lab UPN domain, a group allowlist, and UI confirmation.

Recruiter summary: “The project now connects IAM workflows to an Entra-shaped provider boundary and is ready for a dedicated Microsoft Graph lab without making live cloud access necessary for the demo.”

Technical-interviewer proof points: provider isolation, `/.default` scope, least-privilege permission separation, human versus workload identity, safe error handling, local cache freshness, explicit live-write gates, and truthful license/permission limitations.

Do not describe mocked tests as a live tenant validation. If the audit endpoint is unavailable, demonstrate the limitation message and explain the required permission/role rather than claiming success.

---

# Phase 6 — Azure Identity and RBAC Demo

1. Start in `SIMULATION` and open **Azure Access**.
2. Synchronize Azure RBAC and point out the resource-group boundary and last synchronization time.
3. In **RBAC Assignments**, explain principal + role + scope.
4. Demonstrate Developers → `stcilampdev` → blob read = `ALLOWED`; blob write and archive read = `NOT GRANTED`.
5. Demonstrate `reporting-api-mi` → Key Vault → secret read = `ALLOWED`; RBAC management = `NOT GRANTED`.
6. Explain under **Managed Identities** that Azure supplies workload authentication while RBAC supplies authorization.
7. Contrast the static-secret anti-pattern with managed identity at narrow scope.
8. Finish with **Azure Operations** and its correlation ID.

Recruiter summary: “CILAMP demonstrates Azure resource authorization, least-privilege scope, management/data-plane separation, and credential-free workload identity through a simulation-first control center.”

Technical-interviewer proof points: resource hierarchy, inherited scope, role-assignment anatomy, managed identity, no-secret design, read-only ARM discovery, token-tenant validation, sanitized provider errors, and honest `UNKNOWN` outcomes.

Do not describe the local evaluator as Azure's enforcement engine or claim a live Azure result unless an actual lab synchronization succeeded.

---

# Phase 7 — AWS IAM Demo

1. Start in `SIMULATION`, open **AWS Access**, and synchronize.
2. Show that all three identities are roles using temporary STS sessions, not IAM users with stored keys.
3. In **Policies**, explain Effect + Action + Resource and the different S3 bucket/object ARNs.
4. Show Developer → development object → `s3:GetObject` = `ALLOWED`.
5. Show the same object → `s3:DeleteObject` = `EXPLICIT DENY` and `iam:CreateUser` = `NOT GRANTED`.
6. Show a reporting object is outside the developer policy's resource boundary.
7. Explain STS and contrast hardcoded keys with role-based temporary credentials.
8. Show the selected CloudTrail event metadata and AWS operation correlation ID.

Recruiter summary: “CILAMP applies the same least-privilege ideas across AWS IAM while teaching roles, policy statements, resource scoping, temporary STS credentials, and audit evidence.”

Do not claim the cached evaluator is AWS's enforcement engine or that mocks prove a live AWS account works. Resource policies and organization/session controls remain external inputs.

---
