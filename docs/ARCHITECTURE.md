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
│   ├── security.py           Scenario definitions and troubleshooting rules
│   ├── security_service.py   Security case creation/remediation coordination
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

Access-review findings are calculated from current state rather than stored as a second source of truth. Phase 4 separately persists security-case workflow status and evidence.

## 9.5 Phase 4 Security and Audit Flow

```text
Controlled scenario preview + confirmation
                    ↓
        Simulated security state change
                    ├── immutable audit events
                    └── persisted security finding
                                  ↓
           filter / timeline / privileged activity
                                  ↓
                 troubleshooting checklist
                                  ↓ confirmation
       policy reconciliation or workload posture resolution
                                  ↓
            remediated case + correlated audit evidence
```

Schema version 4 adds `security_findings`, which stores investigation status and evidence metadata. It does not replace derived access-review findings. Audit events remain evidence of what occurred; security findings track whether an observed case is open or remediated.

`security.py` defines the six simulation plans and scenario-specific troubleshooting steps. `security_service.py` coordinates scenario execution and remediation. `repository.py` applies local changes transactionally, persists cases, and records both the successful scenario operation and the accurately failed security/access check.

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

---

# 14. Phase 5 Microsoft Entra Integration

```text
Provider-independent Entra service
              │
              ├── SIMULATION ── local fictional organization
              │
              └── LIVE_LAB ─── Microsoft Graph v1.0 adapter
                                      │
                                      └── Azure CLI / DefaultAzureCredential
              │
              ▼
SQLite display cache + append-only Entra operation history
              │
              ▼
Microsoft Entra dashboard page
```

The connector contract lives under `src/cilamp/connectors/entra/`. Microsoft Graph URLs, token acquisition, pagination, and response translation stay in `graph.py`; lifecycle and policy modules do not import Microsoft APIs. `entra_service.py` applies mode, confirmation, UPN-domain, and group-allowlist controls. `entra_repository.py` stores a replaceable synchronization cache and a separate operation history.

Schema version 5 adds cached users, groups, memberships, service principals, directory audits, synchronization state, and Entra operations. Tokens and credential values are never part of these records.

Live reads use explicit Graph v1.0 endpoints. User profile and membership writes are deliberately narrow: the operator must enable live writes outside the UI, select a synchronized identity, remain inside the configured lab UPN domain, target an allowlisted group where applicable, and confirm the action in the dashboard. Creating users is not automated because it would require handling initial credentials; this phase favors safe selected-user updates.

The cache is a display/investigation projection, not an IAM source of truth. A failed synchronization preserves truthful failure history and never becomes a simulated success. Directory audit retrieval is optional because tenant roles, consent, retention, and licensing can limit availability.

---

# 15. Phase 6 Azure Identity and RBAC

```text
Azure authorization intent / investigation
                  │
          Azure service boundary
             ┌────┴────┐
             │         │
       SIMULATION   LIVE_LAB read-only
             │         │
      fixed lab model  Azure Resource Manager
             └────┬────┘
                  ▼
 resources + principals + role assignments + scopes
                  │
      provider-independent access evaluator
                  │
       ALLOWED / NOT GRANTED / UNKNOWN
                  │
        SQLite cache + Azure Access UI
```

`src/cilamp/connectors/azure/` contains the simulation and Azure Resource Manager adapters. Live discovery is restricted to one configured resource group and performs GET requests only for resources, user-assigned/system-assigned managed identity metadata, role definitions, and applicable role assignments. Tokens are acquired externally through Azure Identity, tenant-checked in memory, and never stored.

`azure_policy.py` explains effective access from principal + role + applicable scope. The simulation catalog distinguishes management-plane `Reader`/`Owner` from data-plane roles such as `Storage Blob Data Reader` and `Key Vault Secrets User`. Lack of a known grant is reported as `NOT GRANTED`, not as an explicit Azure deny. Custom, unknown, or conditional roles produce `UNKNOWN` so the local model does not fabricate certainty.

Schema version 6 adds Azure resources, identities, role assignments, synchronization state, and operation history. These tables are a timestamped investigation/display projection, not Azure's enforcement point.
