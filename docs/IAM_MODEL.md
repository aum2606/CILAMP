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

# 8. Model Status

Implemented in Phase 1:

- Group naming convention.
- Permission catalog.
- Application sensitivity.
- Privileged vs non-privileged role flag.
- Department-to-role compatibility.

Possible later additions, only when justified by a lifecycle scenario:

- Manager hierarchy.
- Contractors and temporary workers.

---

# 9. Phase 1 Implemented Model

The executable source of truth is `src/cilamp/iam_catalog.py`. This document explains that catalog in business terms.

## 9.1 Group Naming Convention

Human-readable group names are used in simulation mode so the IAM story is clear during demonstrations:

- `All Employees` provides baseline access.
- Department groups use the department name, such as `Engineering` or `Finance`.
- Functional groups use plural role/purpose names, such as `Developers` or `Finance Approvers`.
- Privileged groups identify their function explicitly, such as `IT Administrators` and `Security Administrators`.

Cloud-specific naming conventions will be defined with the relevant Entra/Azure/AWS connector instead of being guessed during local simulation.

## 9.2 Implemented Access Matrix

| Role | Groups beyond baseline | Applications beyond Internal Portal | Effective permissions | Privileged |
|---|---|---|---|---|
| Developer | Engineering, Developers | GitHub, Jira, Azure Portal, AWS Console | source.read_write, issues.manage, cloud.dev.read | No |
| Engineering Manager | Engineering, People Managers | GitHub, Jira, Azure Portal | source.read_write, issues.manage, engineering.reports, cloud.dev.read | No |
| Finance Analyst | Finance | Finance Portal | finance.read | No |
| Finance Manager | Finance, Finance Approvers, People Managers | Finance Portal | finance.read, finance.approve | No |
| HR Administrator | HR, HR Administrators | HR Portal | hr.manage | Yes |
| Sales User | Sales | CRM | crm.use | No |
| Sales Manager | Sales, People Managers | CRM | crm.use, crm.reports | No |
| IT Administrator | IT, IT Administrators | Jira, Azure Portal, AWS Console | issues.manage, cloud.ops.scoped | Yes |
| Security Administrator | IT, Security Administrators | Security Center, Azure Portal, AWS Console | security.audit | Yes |
| Marketing User | Marketing | Marketing Hub | marketing.manage | No |

Every role also receives `internal.read` through the baseline model. An application assignment such as Azure Portal or AWS Console does not itself mean cloud administration; the permission catalog determines allowed operations.

## 9.3 Employee Population

The deterministic simulation seed creates exactly 500 active fictional identities:

| Role | Employees |
|---|---:|
| Developer | 120 |
| Engineering Manager | 30 |
| Finance Analyst | 55 |
| Finance Manager | 15 |
| HR Administrator | 35 |
| Sales User | 95 |
| Sales Manager | 25 |
| IT Administrator | 35 |
| Security Administrator | 15 |
| Marketing User | 75 |

Employee IDs and emails are unique. Names are fictional and emails use `example.cilamp`; no real personal or cloud-directory data is present.

## 9.4 Phase 3 Review-Only Permission

`platform.administrator` represents an unrestricted Administrator permission solely for the mandatory excessive-privilege simulation. It is present in the permission catalog so the database can represent the violation, but it is assigned to no approved job role.

The Access Review Center flags this permission as `CRITICAL` whenever it appears. It must never be interpreted as a real Azure, AWS, operating-system, or application administrator role.
