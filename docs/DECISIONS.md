# CILAMP — Architecture Decision Log

## Purpose

This document records important project decisions so that future Claude/Codex sessions do not repeatedly redesign the architecture.

Do not record trivial code choices here.

Use this format for new decisions:

```text
## ADR-XXX — Decision Title

**Date:** YYYY-MM-DD
**Status:** PROPOSED / ACCEPTED / SUPERSEDED

### Context
What problem or decision was required?

### Options Considered
1. Option A
2. Option B

### Decision
What was chosen?

### Reason
Why?

### Trade-offs
What do we gain and what do we give up?

### Consequences
What must future implementation respect?
```

---

# ADR-001 — Project Is Cloud/IAM-First

**Status:** ACCEPTED

## Context

The project owner is targeting Cloud, IAM, Cloud Operations, Cloud Administration, and Cloud Security roles rather than software-development roles.

## Decision

CILAMP will remain primarily an IAM/cloud project.

Custom software exists only to simulate, automate, visualize, and integrate identity operations.

## Reason

A large custom application would shift the portfolio toward software development and reduce focus on identity/security concepts.

## Trade-offs

- Less frontend/backend sophistication.
- More focus on IAM architecture, policy, cloud configuration, troubleshooting, and security.

## Consequences

Do not add complex application features unless they directly support IAM/cloud learning or demonstration.

---

# ADR-002 — UI-First Demonstration

**Status:** ACCEPTED

## Context

The project owner needs to visually verify each phase and demonstrate the project to faculty and interviewers.

## Decision

Each phase must add or improve a Streamlit dashboard or UI view.

CLI may support operations but must not be the main project experience.

## Reason

Visual workflows make JML, RBAC, access reviews, and audit events easier to understand and demonstrate.

## Consequences

Every major capability requires a visual representation.

---

# ADR-003 — Streamlit Instead of React

**Status:** ACCEPTED

## Context

A dashboard is required, but frontend development is not a target career skill.

## Options Considered

1. React frontend + API backend.
2. Streamlit.
3. CLI-only.

## Decision

Use Streamlit.

## Reason

Streamlit allows a professional-enough dashboard with minimal frontend complexity and keeps attention on IAM/cloud concepts.

## Trade-offs

Less frontend flexibility than React.

## Consequences

Do not introduce React unless a future requirement clearly justifies it.

---

# ADR-004 — Simulation Before Live Cloud

**Status:** ACCEPTED

## Context

Cloud identity APIs require credentials, permissions, licensing, and careful security controls.

## Decision

All core IAM logic must work in local simulation mode before live Entra/Azure/AWS integration.

## Reason

This allows safe development, reliable testing, and demonstrations without cloud dependencies.

## Consequences

Live connectors must implement the same domain operations as simulation connectors rather than redefining the lifecycle logic.

---

# ADR-005 — Repository Is the Long-Term AI Memory

**Status:** ACCEPTED

## Context

Claude/Codex conversations may change, reset, or lose previous chat context.

## Decision

Project memory is stored in version-controlled repository files.

Primary state files:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/PROJECT_STATE.md`
- `docs/ROADMAP.md`
- `docs/DECISIONS.md`

## Reason

Repository state is persistent, reviewable, and tool-independent.

## Consequences

Every meaningful development session must update project state before completion.

Conversation memory never overrides committed repository state without discussion.

---

# ADR-006 — One Agent Owns a Phase at a Time

**Status:** ACCEPTED

## Context

Claude and Codex may both be used.

## Decision

Do not allow multiple AI agents to edit the same branch simultaneously.

One agent owns a phase or unit of work until it has tested, documented, and committed its changes.

## Reason

Avoid conflicting architectures and inconsistent project memory.

## Consequences

Switch agents only from a clean Git state whenever possible.

---

# ADR-007 — Separate Domain Logic from Cloud Connectors

**Status:** ACCEPTED

## Context

The same lifecycle logic needs to work locally and across Entra/Azure/AWS.

## Decision

Cloud-specific API calls must live in connector modules.

Core lifecycle/policy logic must be provider-independent.

## Reason

Improves testability, portability, and conceptual clarity.

## Consequences

Lifecycle functions should request operations through interfaces/services rather than calling Graph/boto3 directly.

---

# ADR-008 — SQLite First

**Status:** ACCEPTED

## Context

The project needs persistent local state but does not initially need production database infrastructure.

## Decision

Use SQLite initially.

PostgreSQL may be introduced later only if there is a clear deployment reason.

## Reason

Simple setup, no additional service, adequate for simulation.

## Trade-offs

Not intended as the final enterprise-scale database architecture.

---

# ADR-009 — No Hardcoded Secrets

**Status:** ACCEPTED

## Context

The project explicitly teaches secure human and workload identity.

## Decision

Secrets must never be committed to Git.

Use environment variables, local cloud credential stores, SSO, managed identities, or appropriately scoped service principals.

## Consequences

`.env` must be ignored.

Only `.env.example` with placeholders may be committed.

---

# ADR-010 — Terraform Is Added After Manual Understanding

**Status:** ACCEPTED

## Context

Infrastructure as Code is useful but can hide cloud concepts if introduced too early.

## Decision

Terraform will be introduced only after relevant Azure/AWS IAM concepts are understood and demonstrated manually.

## Reason

The project owner must understand what infrastructure and permissions Terraform is creating.

---

# ADR-011 — No Kubernetes in Core Scope

**Status:** ACCEPTED

## Context

Kubernetes could add complexity unrelated to the immediate Cloud/IAM goal.

## Decision

Kubernetes is excluded from the main roadmap.

## Consequences

It may be added as an optional extension only after core project completion.

---

# ADR-012 — Phase 0 Rejects Live Lab Mode

**Date:** 2026-09-03
**Status:** ACCEPTED

## Context

The foundation has no reviewed cloud connectors, cloud permissions, or live-write confirmation workflow. Merely displaying a live mode would create a misleading safety signal.

## Options Considered

1. Accept `LIVE_LAB` but leave connectors disconnected.
2. Ignore the configured mode and always display simulation.
3. Reject any mode other than `SIMULATION` until a live integration phase is approved.

## Decision

Phase 0 validates configuration at startup and rejects non-simulation mode.

## Reason

Failing closed makes the runtime state unambiguous and prevents an unsupported configuration from appearing operational.

## Trade-offs

Live mode cannot be previewed early. A later cloud-integration phase must deliberately expand the allowed mode and add confirmation controls.

## Consequences

Future live-lab work must update configuration validation, the security model, tests, and the dashboard together.

---

# ADR-013 — Deterministic Role-Driven Organization Seed

**Date:** 2026-09-04

**Status:** ACCEPTED

## Context

Phase 1 needs a repeatable 500-employee enterprise model for demonstrations and tests without introducing real personal data or a data-generation dependency.

## Options Considered

1. Randomly generate employees on every startup.
2. Commit a large CSV containing 500 identities.
3. Generate deterministic fictional identities from a small role distribution and name catalog.

## Decision

Use deterministic generation and persist the resulting identities idempotently in SQLite. Expected groups, applications, and permissions are derived from a single role catalog.

## Reason

The same identity always has the same role and expected access, making IAM demonstrations, tests, and troubleshooting reproducible. The compact catalog remains easier to review than a large committed dataset.

## Trade-offs

The population is representative rather than statistically realistic, and all Phase 1 employees are active. Lifecycle-driven status changes belong to Phase 2.

## Consequences

Changes to roles or seeded distributions require corresponding IAM documentation and tests. Random access assignment and direct user grants must not be introduced as default behavior.

---

# ADR-014 — Previewed, Transactional Lifecycle Operations

**Date:** 2026-09-04

**Status:** ACCEPTED

## Context

JML operations change identity state and multiple access assignments. Operators need to understand the impact before execution, Movers must not accumulate access, and partial changes must not leave an identity inconsistent.

## Options Considered

1. Apply changes immediately from each form.
2. Preview changes but execute each assignment independently.
3. Build a provider-independent plan, require confirmation, and apply it atomically.

## Decision

Every Phase 2 operation produces a before/after plan and explicit access deltas. The dashboard requires confirmation, and the repository executes the plan in one transaction with correlated audit events. Mover revocations occur before grants.

## Reason

This makes least privilege visible, prevents partial local state, supports troubleshooting, and mirrors the change-control discipline expected for later cloud integrations.

## Trade-offs

The local transaction cannot guarantee atomicity across future cloud APIs. Live connectors will require compensating actions, reconciliation, idempotency, and truthful partial-failure reporting.

## Consequences

Cloud connectors must consume approved lifecycle intent without embedding or redefining the JML business rules. A stale preview must be regenerated before execution.

---

# ADR-015 — Findings Are Derived from Current Expected vs Actual Access

**Date:** 2026-09-04

**Status:** ACCEPTED

## Context

Access review needs a reliable answer to whether an identity's assignments are justified. Persisting a separate finding record for every comparison could become stale whenever lifecycle or policy state changes.

## Options Considered

1. Store manually authored findings.
2. Store every computed finding and synchronize it after all changes.
3. Calculate findings from the authoritative role baseline and current assignments when reviewed.

## Decision

Phase 3 derives findings at review time. Remediation reconciles actual assignments to expected access in one transaction, requires confirmation, and records audit evidence rather than treating findings as authoritative state.

## Reason

The role catalog and actual assignments remain the two review inputs. Findings cannot silently outlive the state that produced them, and stale remediation is rejected.

## Trade-offs

Reviewing all 500 local identities performs more reads than loading a cached finding table. This is acceptable for the simulation scale. Phase 4 may persist security workflow metadata without replacing current-state evaluation.

## Consequences

Future cloud reviews must clearly identify the timestamp/source of actual state. Exceptions require an explicit design and justification rather than suppressing findings informally.

---

# ADR-016 — Separate Immutable Audit Evidence from Mutable Case Status

**Date:** 2026-09-04

**Status:** ACCEPTED

## Context

Security operations need both a historical record of events and a workflow indicating whether a finding is still open. Updating an audit record to mark a case fixed would destroy evidence; treating every derived policy variance as a stored case would create stale duplicates.

## Options Considered

1. Use audit events as mutable case records.
2. Persist every access-review variance as a finding.
3. Keep append-only audit evidence, derive access reviews from current state, and persist only explicit security cases with lifecycle status.

## Decision

Audit events are immutable evidence. Access-review findings remain derived. Confirmed Phase 4 scenarios create persisted security findings that transition from `OPEN` to `REMEDIATED` while resolution actions append new audit events.

## Reason

This preserves historical truth, avoids stale policy snapshots, and supports an understandable investigation workflow.

## Trade-offs

The dashboard correlates three related views: current policy evaluation, historical events, and case status. This extra distinction reflects real security operations and prevents misleading data mutation.

## Consequences

Future cloud events must retain truthful provider results. A failed provider action must never be rewritten as successful merely because a later retry succeeds.

---

# ADR-017 — Use a Guarded Graph Adapter and Replaceable Entra Cache

**Date:** 2026-09-04

**Status:** ACCEPTED

## Context

Phase 5 needs a useful simulation and a real Microsoft Entra lab path without coupling provider behavior to JML policy or allowing a dashboard toggle to authorize cloud writes.

## Options Considered

1. Put Microsoft Graph calls directly in Streamlit and lifecycle functions.
2. Require client secrets and write directly to Graph with no local projection.
3. Use a provider contract with simulation/Graph adapters, external identity credentials, a local display cache, and service-level safety gates.

## Decision

Use option 3. `AzureCliCredential` is the default local live-lab authentication path; `DefaultAzureCredential` supports managed/workload identity deployment. Both request the Graph `/.default` scope for an explicitly configured lab tenant, and the adapter checks the returned token's tenant claim. No secret-based credential is accepted by CILAMP.

Live writes require all of: `LIVE_LAB`, the dedicated-lab startup guard, a separate write-enable setting, a synchronized target, an allowed UPN suffix, an allowed group ID for membership changes, and an in-dashboard confirmation. The supported writes are profile metadata updates and group membership changes.

## Reason

The design keeps cloud translation replaceable, provides offline demonstrations, makes least privilege visible, and prevents a UI-only action from expanding the application's authority.

## Trade-offs

The local cache can become stale and is not a transactional mirror of Entra. User creation is excluded to avoid handling initial passwords. Live behavior depends on consent, directory roles, tenant licensing, and network access, so mocked Graph tests do not constitute a live success claim.

## Consequences

Operators must synchronize before selecting targets and reconcile after writes. Provider failures are recorded as failures. Future lifecycle-to-Entra automation must consume approved domain intent through this boundary and add idempotency/partial-failure handling rather than bypassing it.
