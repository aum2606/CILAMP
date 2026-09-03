# CILAMP — IAM Model

## Purpose

This document defines the business access model that drives the platform.

It should evolve during Phase 1 and become the authoritative description of departments, roles, groups, applications, and permissions.

---

# 1. Fictional Organization

Target size:

**Approximately 500 employees**

Departments:

- Engineering
- Finance
- HR
- Sales
- IT
- Marketing

---

# 2. Initial Role Model

## Engineering

### Developer

Typical access:

- Engineering group.
- Developer group.
- GitHub.
- Jira.
- Development cloud resources.

Should not automatically receive:

- Finance applications.
- HR administration.
- Azure subscription Owner.
- AWS AdministratorAccess.

### Engineering Manager

Typical access:

- Engineering group.
- Manager group.
- GitHub.
- Jira.
- Team management resources.
- Selected reporting access.

---

## Finance

### Finance Analyst

Typical access:

- Finance group.
- Finance application.
- Selected reporting resources.

Should not receive:

- Engineering development access.
- HR administration.
- Cloud administration.

### Finance Manager

Typical access:

- Finance group.
- Finance manager group.
- Finance application.
- Finance reporting/approval permissions.

---

## HR

### HR Administrator

Typical access:

- HR group.
- HR application.
- Employee-management permissions.

Should not automatically receive:

- Cloud infrastructure administration.
- Engineering development access.

---

## Sales

### Sales User

Typical access:

- Sales group.
- CRM.
- Sales applications.

### Sales Manager

Typical access:

- Sales group.
- Manager group.
- CRM.
- Sales reporting/approval access.

---

## IT

### IT Administrator

Typical access:

- IT group.
- Infrastructure-management permissions.
- Selected Azure/AWS administrative capabilities.

Must still follow least privilege.

### Security Administrator

Typical access:

- Security group.
- Security/audit tools.
- Identity/security administration where justified.

Must be treated as privileged.

---

## Marketing

### Marketing User

Typical access:

- Marketing group.
- Marketing applications.
- Content/campaign systems.

---

# 3. Application Model

Initial fictional applications:

| Application | Primary Users |
|---|---|
| GitHub | Engineering |
| Jira | Engineering / selected IT |
| CRM | Sales |
| HR Portal | HR |
| Finance Portal | Finance |
| Azure Portal | Selected IT / Engineering |
| AWS Console | Selected IT / Engineering |
| Internal Portal | General employees |

---

# 4. Access Design Rules

1. Access comes primarily from job role.
2. Department determines the business context.
3. Groups are preferred over individual grants.
4. Privileged access is never granted automatically to normal users.
5. Mover removes obsolete access.
6. Leaver removes active access.
7. Direct grants should be clearly visible and reviewable.
8. Cloud permissions must follow least privilege.

---

# 5. Initial Access Matrix

This is a starter model and should be refined during Phase 1.

| Role | GitHub | Jira | CRM | HR Portal | Finance Portal | Azure | AWS |
|---|---:|---:|---:|---:|---:|---:|---:|
| Developer | Yes | Yes | No | No | No | Limited | Limited |
| Engineering Manager | Yes | Yes | No | No | No | Limited | Limited |
| Finance Analyst | No | No | No | No | Yes | No | No |
| Finance Manager | No | No | No | No | Yes | No | No |
| HR Administrator | No | No | No | Yes | No | No | No |
| Sales User | No | No | Yes | No | No | No | No |
| Sales Manager | No | No | Yes | No | No | No | No |
| IT Administrator | Optional | Yes | Optional | No | No | Admin/Scoped | Admin/Scoped |
| Security Administrator | No | Optional | No | No | No | Security/Scoped | Security/Scoped |
| Marketing User | No | No | Optional | No | No | No | No |

---

# 6. Privileged Access

Privileged roles may include:

- IT Administrator.
- Security Administrator.
- Azure Owner/User Access Administrator where explicitly required.
- AWS IAM administration where explicitly required.

CILAMP should flag privileged assignments that are inconsistent with the user's role.

---

# 7. Direct Assignment Rule

If an employee receives a direct permission outside their role/group model, CILAMP should mark it as:

```text
DIRECT ASSIGNMENT
```

and make it visible during access review.

It is not automatically wrong, but it requires justification.

---

# 8. Future Enhancements

During Phase 1, add:

- Group naming convention.
- Permission catalog.
- Application sensitivity.
- Privileged vs non-privileged role flag.
- Department-to-role compatibility.
- Manager hierarchy if useful.
- Sample contractors/temporary workers if useful.
