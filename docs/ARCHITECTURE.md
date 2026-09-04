# CILAMP — Architecture

## 1. Purpose

CILAMP is a Cloud Identity Lifecycle & Access Management Platform designed to simulate and later integrate enterprise identity operations across Microsoft Entra ID, Azure, and AWS.

The architecture prioritizes:

- IAM concepts over application complexity.
- Separation of business logic from cloud APIs.
- Simulation-first development.
- Safe live lab integration.
- Visual verification through Streamlit.
- Auditability.
- Least privilege.
- Replaceable cloud connectors.

---

# 2. High-Level Architecture

```text
                    HR / Employee Source
                           │
                           ▼
                ┌──────────────────────┐
                │ Identity Lifecycle   │
                │ Engine               │
                └──────────┬───────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           JOINER        MOVER        LEAVER
              │            │            │
              └────────────┼────────────┘
                           ▼
                 ┌──────────────────┐
                 │ Policy / RBAC    │
                 │ Engine           │
                 └────────┬─────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
 Microsoft Entra       Azure            AWS IAM
    Connector         Connector         Connector
        │                 │                 │
        └─────────────────┼─────────────────┘
                          ▼
                  ┌───────────────┐
                  │ Audit Engine  │
                  └───────┬───────┘
                          ▼
                  Streamlit Dashboard
```

---

# 3. Architectural Layers

## 3.1 Presentation Layer

**Technology:** Streamlit

Responsibilities:

- Dashboard.
- Employee search.
- Employee profile.
- JML forms.
- Before/after access comparison.
- Access review.
- Security alerts.
- Audit history.
- Cloud connector status.
- System health.

The presentation layer must not contain core IAM business rules.

---

## 3.2 Domain Layer

Contains the core IAM concepts.

Suggested entities:

- Employee
- Department
- JobRole
- Group
- Application
- Permission
- AccessPolicy
- LifecycleEvent
- AuditEvent

This layer should remain independent from Azure/AWS SDKs.

---

## 3.3 Lifecycle Layer

Implements:

- Joiner.
- Mover.
- Leaver.

Responsibilities:

- Determine desired access.
- Compare desired access vs current access.
- Generate changes.
- Enforce removal-before-grant behavior for movers.
- Disable and revoke access for leavers.

---

## 3.4 Policy / Authorization Layer

Responsibilities:

- RBAC evaluation.
- Least-privilege validation.
- Expected-access calculation.
- Actual-access comparison.
- Excess privilege detection.
- Stale access detection.
- Privilege creep detection.

---

## 3.5 Connector Layer

Cloud-specific implementation lives here.

Suggested layout:

```text
connectors/
├── entra/
├── azure/
└── aws/
```

Each connector translates domain actions into provider-specific API calls.

Example:

```text
Domain instruction:
"Add employee to Engineering group"

Entra connector:
Microsoft Graph group membership operation
```

The lifecycle engine should not directly call Microsoft Graph or boto3.

---

## 3.6 Data Layer

Initial implementation:

**SQLite**

Possible later implementation:

**PostgreSQL**

Responsibilities:

- Employee state.
- Group membership.
- Role assignment.
- Application access.
- Lifecycle history.
- Audit history.
- Security findings.
- Integration metadata.

---

## 3.7 Audit Layer

Every important operation should create an audit event.

Suggested fields:

- event_id
- timestamp
- actor
- target_identity
- action
- old_state
- new_state
- result
- reason
- source
- correlation_id

---

# 4. Core Data Relationships

```text
Employee
  │
  ├── belongs to → Department
  │
  ├── assigned → Job Role
  │
  ├── member of → Groups
  │
  ├── granted → Applications
  │
  └── receives → Permissions

Job Role
  │
  ├── maps to → Groups
  ├── maps to → Applications
  └── maps to → Permissions
```

The access model should be driven primarily by role/department rules rather than manually assigning random permissions to individual users.

---

# 5. Joiner Flow

```text
New Employee
    ↓
Validate employee record
    ↓
Determine department + role
    ↓
Resolve required groups
    ↓
Resolve required applications
    ↓
Resolve required permissions
    ↓
Create identity state
    ↓
Apply access
    ↓
Validate least privilege
    ↓
Audit operation
```

---

# 6. Mover Flow

```text
Existing Employee
    ↓
New department/role
    ↓
Calculate current access
    ↓
Calculate desired access
    ↓
Determine access to REMOVE
    ↓
Remove obsolete access
    ↓
Determine access to ADD
    ↓
Grant new access
    ↓
Run privilege validation
    ↓
Audit before/after state
```

Removal-before-grant is preferred to reduce temporary privilege accumulation.

---

# 7. Leaver Flow

```text
Employee Termination
    ↓
Disable identity
    ↓
Revoke active permissions
    ↓
Remove groups
    ↓
Remove application access
    ↓
Invalidate cloud access where applicable
    ↓
Preserve audit/history
    ↓
Mark employee disabled
```

---

# 8. Simulation vs Live Lab

## Simulation Mode

Default mode.

Uses:

- Fictional users.
- Local database.
- Local policy engine.
- Mock cloud connectors.

Benefits:

- Safe.
- Fast.
- Demo-friendly.
- No paid cloud dependency.
- Easy to test failure scenarios.

## Live Lab Mode

Used only after simulation logic is stable.

Requirements:

- Dedicated lab account/tenant.
- Least-privileged identity.
- Explicit confirmation for significant write operations.
- No production resources.
- No root or global-admin-by-default approach.

The UI must clearly display the current mode.

---

# 9. Repository Structure

The repository currently contains the Phase 0 foundation and Phase 1 organization model:

```text
CILAMP/
├── AGENTS.md                 Persistent Codex/agent rules
├── CLAUDE.md                 Concise Claude Code entry point
├── README.md                 Startup and verification instructions
├── pyproject.toml            Python package and test configuration
├── .env.example              Placeholder-only local configuration
├── dashboard/
│   └── app.py                Streamlit Project Control Center
├── src/cilamp/
│   ├── config.py             Simulation-only configuration boundary
│   ├── database.py           SQLite initialization and health
│   ├── domain.py             Provider-independent identity/access objects
│   ├── iam_catalog.py        Authoritative expected-access catalog
│   ├── lifecycle.py          Provider-independent JML planning rules
│   ├── lifecycle_service.py  Input validation and operation coordination
│   ├── policy.py             RBAC evaluation and access explanations
│   ├── access_review_service.py  Review/scenario/remediation coordination
│   ├── organization.py       Deterministic fictional HR source
│   ├── repository.py         Organization persistence and queries
│   └── project_status.py     Phase/module presentation metadata
├── data/                     Ignored local SQLite runtime data
├── tests/                    Phase 0 automated checks
└── docs/                     Project memory and IAM documentation
```

Lifecycle, policy, audit, service, and connector packages are added only when their roadmap phase requires them. This avoids empty architecture and keeps cloud-provider APIs out of the organization model.

## 9.1 Phase 0 Runtime Flow

```text
Streamlit Project Control Center
          ↓
Simulation-only settings validation
          ↓
SQLite idempotent initialization
          ↓
Database/system/module health presentation
```

The Phase 2 database uses schema version 3. It contains normalized catalogs, actual employee assignment tables, and lifecycle audit events. A deterministic seed creates exactly 500 fictional active employees and grants their initial role access once. The seed marker prevents a future application restart from restoring access revoked by a Leaver operation.

## 9.2 Phase 1 Runtime Flow

```text
Authoritative IAM catalog
  department + compatible job role
                 ↓
        Deterministic employee seed
                 ↓
         Normalized SQLite store
                 ↓
 Search/filter + effective role access
                 ↓
 Streamlit Organization Explorer / Access Matrix
```

`domain.py` defines provider-independent identity and access objects. `iam_catalog.py` defines expected access policy, `organization.py` creates fictional source identities, and `repository.py` owns SQLite persistence and queries. No Microsoft, Azure, or AWS APIs are present.

## 9.3 Phase 2 Lifecycle Flow

```text
Operator input
     ↓
Provider-independent preview plan
     ├── identity before / after
     ├── access to remove
     └── access to add
     ↓ explicit confirmation
Transactional local execution
     ├── Joiner: create → grant
     ├── Mover: revoke → update → grant
     └── Leaver: disable → revoke all
     ↓
Correlated audit events + resulting identity
```

`lifecycle.py` owns transition and access-difference rules. `lifecycle_service.py` validates application input and coordinates persistence. `repository.py` applies a confirmed plan atomically and rejects stale previews if persisted identity or access state changed. The execution layer contains no cloud-provider calls.

Expected role access and actual assigned access are distinct, enabling Phase 3 access review.

## 9.4 Phase 3 Access Review Flow

```text
Job role + identity status                Persisted assignments
          ↓                                       ↓
   Expected access                          Actual access
          └────────────── compare ────────────────┘
                              ↓
        match / excess / missing / unauthorized / stale
                              ↓
        risk + explanation + suggested remediation
                              ↓ explicit confirmation
             reconcile actual access to role baseline
                              ↓
                 correlated audit evidence
```

`policy.py` is a pure evaluation layer. It identifies excessive privilege, unauthorized groups/applications, stale permission/privilege creep, missing access, and privileged identities. `access_review_service.py` loads reviews and coordinates controlled scenarios/remediation. The repository applies remediation transactionally and rejects stale reviews.

Findings are calculated from current state rather than stored as a second source of truth. Phase 4 may persist security-event workflow state when the Security & Audit Center requires it.

---

# 10. Integration Architecture

## Microsoft Entra

```text
CILAMP
  ↓
Entra Connector
  ↓
Microsoft Graph
  ↓
Microsoft Entra ID
```

Potential operations:

- Users.
- Groups.
- Membership.
- Applications.
- Service principals.
- Audit/sign-in information.

---

## Azure

```text
CILAMP
  ↓
Azure Connector
  ↓
Azure APIs / SDK
  ↓
Azure Resources
```

Focus:

- RBAC.
- Scope.
- Managed identities.
- Key Vault.
- Storage.

---

## AWS

```text
CILAMP
  ↓
AWS Connector
  ↓
boto3 / AWS APIs
  ↓
AWS IAM / S3 / CloudTrail
```

Focus:

- Roles.
- Policies.
- Effective access.
- STS concepts.
- Audit.

---

# 11. Non-Human Identity Model

The project must distinguish:

## Human Identity

```text
Employee
  ↓
Entra ID / IAM identity
  ↓
MFA
  ↓
RBAC
  ↓
Application / Cloud Resource
```

## Workload Identity

```text
Application
  ↓
Managed Identity / Service Principal / IAM Role
  ↓
Authorization
  ↓
Cloud Resource
```

Avoid:

```text
Application
  ↓
Hardcoded password/key
  ↓
Cloud Resource
```

---

# 12. Architectural Constraints

1. Do not build a complex frontend.
2. Do not introduce microservices without a genuine need.
3. Do not make the CLI the primary demonstration surface.
4. Do not mix cloud SDK calls into core lifecycle logic.
5. Do not require live cloud access for basic project demonstration.
6. Do not commit secrets.
7. Do not assume premium cloud identity licensing.
8. Do not represent unavailable paid features as implemented live.
9. Keep the project understandable to a Cloud/IAM candidate.
10. Prefer simple, testable components over clever abstractions.

---

# 13. Future Architecture Decisions

Any major change must be recorded in `DECISIONS.md`.

Examples:

- Switching database.
- Changing UI framework.
- Adding a new cloud.
- Introducing background workers.
- Adding API server.
- Changing authentication architecture.
- Changing repository layout.
