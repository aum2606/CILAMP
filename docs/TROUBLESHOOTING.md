# CILAMP — Troubleshooting Guide

## Purpose

This file records operational troubleshooting workflows for both the project itself and IAM scenarios.

Claude/Codex should add real issues encountered during development instead of repeatedly solving the same problem from scratch.

---

# 1. General Troubleshooting Method

Use:

```text
Problem
   ↓
Identify affected component
   ↓
Check expected state
   ↓
Check actual state
   ↓
Review logs/audit
   ↓
Validate configuration
   ↓
Apply smallest safe fix
   ↓
Retest
   ↓
Document root cause
```

---

# 2. Dashboard Does Not Start

## Check

1. Python environment activated?
2. Dependencies installed?
3. Correct working directory?
4. Streamlit installed?
5. Correct app path?
6. Syntax/import error?

## Typical Command

```bash
streamlit run dashboard/app.py
```

## Verify

- Browser opens.
- CILAMP page loads.
- Application health is healthy.

---

# 3. Database Error

## Symptoms

- Dashboard launches but employee data does not load.
- SQLite file missing.
- Schema error.

## Check

1. Database path.
2. File permissions.
3. Initialization/migration function.
4. Schema version.
5. Application logs.

## Safe Recovery

For simulation-only development, recreate the local DB only if documented and if no important state must be preserved.

Never automatically delete data in live environments.

---

# 4. Employee Cannot Access Application

Use this IAM flow:

```text
Does employee exist?
      ↓
Is employee active?
      ↓
Correct department?
      ↓
Correct job role?
      ↓
Correct group membership?
      ↓
Application assigned?
      ↓
Required permission present?
      ↓
Authentication/MFA issue?
      ↓
Conditional Access/security policy?
      ↓
Cloud role/policy correct?
      ↓
Review audit/logs
```

Document the root cause.

---

# 5. Employee Has Too Much Access

## Check

1. Expected role.
2. Expected groups.
3. Actual groups.
4. Direct permission assignments.
5. Previous department permissions.
6. Privileged role assignments.
7. Cloud-specific role/policy.

## Likely Causes

- Mover workflow did not remove old access.
- Direct manual grant.
- Incorrect role mapping.
- Incorrect group membership.
- Overly broad cloud policy.

## Corrective Action

Remove only access that is not justified.

Record remediation in audit history.

---

# 6. Mover Retains Old Access

## Expected

Old department/role permissions should be removed.

## Check

- `current_access`
- `desired_access`
- calculated `to_remove`
- calculated `to_add`
- audit result

## Potential Bug

Mover logic may be adding new access without computing the old-vs-new difference.

## Required Rule

```text
Current Access
     -
Desired Access
     =
Access To Remove
```

and:

```text
Desired Access
     -
Current Access
     =
Access To Add
```

Remove obsolete access before adding new access.

---

# 7. Leaver Still Has Access

Treat as high severity.

## Check

- Account disabled?
- Groups removed?
- Applications revoked?
- Cloud roles removed?
- Active sessions/tokens conceptually revoked where supported?
- Audit operation successful?

The simulation should flag incomplete offboarding.

---

# 8. Entra Connector Fails

## Check

1. Project is actually in LIVE LAB mode.
2. Tenant configuration.
3. Application/service principal configuration.
4. Required Graph permission.
5. Consent status.
6. Authentication method.
7. Token acquisition.
8. API error response.
9. Network access.

## Important

Do not solve permission errors by automatically granting broad administrator privileges.

Determine the minimum required permission.

---

# 9. Graph API Returns 403

A 403 typically indicates authorization failure.

Check:

- Correct identity used?
- Correct delegated/application permission?
- Admin consent required?
- Resource operation allowed?
- Tenant policy?
- Target object protected?

Document the exact required permission instead of broadening access unnecessarily.

---

# 10. AWS Access Denied

## Check

1. Which identity/role is active?
2. What IAM policy is attached?
3. Resource policy?
4. Permission boundary?
5. SCP if applicable?
6. Explicit deny?
7. Correct resource ARN?
8. Correct region/account?

Remember:

An explicit deny overrides an allow.

Do not fix by giving AdministratorAccess unless the lab scenario explicitly requires administration.

---

# 11. Wrong AWS Credentials/Profile

## Check

- Active AWS profile.
- `aws sts get-caller-identity`
- Expected account.
- Expected role.
- Expired credentials.

Never use root credentials for CILAMP.

---

# 12. Terraform Plan Unexpectedly Destructive

STOP.

Do not apply.

## Check

- Correct workspace/environment.
- State file.
- Provider/account.
- Resource renames.
- Import requirements.
- Configuration drift.

Any plan proposing unexpected deletion must be reviewed manually.

---

# 13. Docker Container Starts but UI Is Unreachable

Check:

- Container running.
- Streamlit binding address.
- Port exposed.
- Port mapped.
- Environment configuration.
- Logs.
- Health check.

---

# 14. Tests Fail After AI Changes

Do not simply delete tests.

Check:

1. Which test failed?
2. Was expected business behavior intentionally changed?
3. Is implementation wrong?
4. Is test outdated?
5. Does the change violate an ADR/security rule?

Prefer fixing the implementation when the test represents an accepted IAM rule.

---

# 15. Git Working Tree Is Dirty Before New Phase

Before starting a new phase:

1. Review `git status`.
2. Review diff.
3. Determine whether changes belong to completed work.
4. Run tests.
5. Commit coherent changes.
6. Avoid mixing unrelated work into next phase.

Do not switch Claude ↔ Codex in the middle of an undocumented dirty state.

---

# 16. AI Agent Seems to Have Lost Context

Do not repeat the entire conversation manually.

Tell the agent to read:

- `AGENTS.md` / `CLAUDE.md`
- `docs/PROJECT_STATE.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/DECISIONS.md`
- recent Git history

Repository state is the project memory.

---

# 17. AI Agent Tries to Build Future Phases

Stop the implementation.

Point to `ROADMAP.md` and `PROJECT_STATE.md`.

Rule:

> Work only on the currently approved phase. Finish, test, document, commit, then stop.

---

# 18. Lifecycle Preview Is Stale

## Symptom

Execution reports that identity state changed after preview.

## Cause

The employee record or actual assignments changed between preview and confirmation. Applying the old plan could overwrite a newer lifecycle decision.

## Resolution

1. Do not bypass the conflict.
2. Reopen the employee and inspect current status and access.
3. Generate a new Joiner, Mover, or Leaver preview.
4. Confirm the new removal/addition sets are still justified.
5. Execute the new plan and retain its correlation ID.

This is an optimistic concurrency safety control, not a reason to broaden permissions.

---

# 19. Incident Record Template

Use this section when a real development issue occurs.

```text
## INCIDENT-XXX — Title

Date:
Phase:
Severity:

### Symptom
What happened?

### Expected Behavior
What should have happened?

### Root Cause
Why did it happen?

### Fix
What was changed?

### Validation
How was the fix tested?

### Prevention
What should prevent recurrence?

### Related Commit
<commit hash>
```

---

# 20. Current Incidents

## INCIDENT-001 — Pytest Temporary Directory Denied in Managed Windows Sandbox

**Date:** 2026-09-03

**Phase:** 0

**Severity:** Low

**Status:** Resolved for validation; environment-specific behavior documented

### Symptom

The initial test run could not create pytest temporary directories under the user profile. A later Streamlit test cleanup also reported an inaccessible generated temporary directory, although all tests passed.

### Expected Behavior

Test fixtures and Streamlit test resources should create and remove temporary artifacts normally.

### Root Cause

The managed execution sandbox restricted access to directories created through Python's temporary-file APIs. This was not a CILAMP database or IAM logic failure.

### Fix

Phase 0 tests use ignored database files under the repository `data/` directory, explicitly close SQLite connections, and disable pytest's cache provider. Validation sets `TEMP` and `TMP` to an approved workspace location when required by the managed sandbox.

### Validation

Seven tests passed, and the running Streamlit health endpoint returned `ok`.

### Prevention

Keep test artifacts in writable locations in restricted CI/sandbox environments. Explicitly close SQLite connections so Windows can release file locks.

### Related Commit

Phase 0 milestone commit.
