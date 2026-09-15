# IAM ConCen

### AWS Cloud Identity & Access Management Platform

IAM ConCen is a centralized Cloud Identity & Access Management (IAM) platform built to demonstrate how organizations manage employee access, enforce security boundaries, and govern identities across their lifecycle. The platform focuses on the operational challenges of modern cloud security: ensuring access is provisioned accurately when people join, adjusted responsibly when they move roles, and revoked immediately when they leave.

By integrating Role-Based Access Control (RBAC), least-privilege policy evaluation, access reviews, audit tracking, and real-time AWS IAM synchronization, IAM ConCen bridges human organizational hierarchy with cloud security controls. It provides security engineers, auditors, and engineering leaders with clear visibility into permissions across enterprise applications and AWS cloud infrastructure.

The platform provides an interactive Streamlit-based command center supporting two operational modes: an offline simulation mode populated with realistic enterprise identity data, and a live AWS lab mode that interfaces with AWS IAM, AWS STS, Amazon S3, and AWS CloudTrail using read-only, scoped permissions.

---

## Project Overview

In fast-growing organizations, managing identity and access manually leads to widespread security and operational friction:

- **Inconsistent and Manual Provisioning**: Access is frequently granted ad-hoc via one-off requests rather than standardized roles, leading to configuration drift.
- **Privilege Creep**: As employees transfer departments or take on temporary duties, new permissions are added while old ones are rarely removed.
- **Orphaned and Stale Access**: Former employees or inactive accounts retain access to cloud resources and sensitive tools after departure.
- **Difficult Access Certification**: Security teams and managers lack clear, centralized visibility to verify who has access to which resources.
- **Fragmented Audit Visibility**: Changes made across identity providers and cloud environments are difficult to correlate without uniform audit logs.

IAM ConCen addresses these challenges by introducing structured identity lifecycle automation, a standardized access matrix, continuous access certification with automated findings, and an explainable AWS policy evaluation engine.

---

## The Core Idea

At its core, IAM ConCen is designed to answer four fundamental identity governance questions:

> **Who has access to what, why do they have it, and should they still have it?**

The platform maps organizational hierarchy directly to technical cloud resources through a clear multi-tiered access model:

```text
Employee
   ↓
Department
   ↓
Job Role
   ↓
Groups & Applications & Permissions
   ↓
AWS Resources & IAM Roles
```

- **Employee**: The individual identity record (name, business email, employee ID, active status).
- **Department**: The business organizational unit (e.g., Engineering, Finance, IT, HR, Sales, Marketing).
- **Job Role**: The formal organizational role that defines baseline access requirements.
- **Groups & Applications & Permissions**: Standardized directory groups, authorized business software, and granular application permissions.
- **AWS Resources & IAM Roles**: Specific cloud targets (such as Amazon S3 buckets or IAM role policies) governed by cloud permissions.

---

## Joiner → Mover → Leaver (JML)

Identity lifecycle management is implemented through the Joiner, Mover, Leaver (JML) workflow. Every transition calculates access diffs before execution and records immutable audit records.

```text
       JOINER
         ↓
Access Provisioning (Baseline Role Assignment)
         ↓
       MOVER
         ↓
Access Review & Adjustment (Remove Old, Grant New)
         ↓
       LEAVER
         ↓
Access Revocation (Disable Identity & Strip Entitlements)
```

### Joiner
When a new team member joins the organization:
1. An identity profile is created with a unique identifier and organizational email.
2. The employee is assigned to their approved department and designated job role.
3. Baseline groups, enterprise applications, and permissions defined in the access catalog are automatically calculated and provisioned.
4. An audit event is generated to document the onboarding action and timestamp.

### Mover
When an employee changes department or transitions into a new role:
1. The platform compares the employee's existing entitlements against the baseline required for the new role.
2. Permissions and group memberships associated solely with the previous role are identified for revocation to prevent privilege creep.
3. Entitlements required for the new role are queued for assignment.
4. The transition is reviewed, confirmed, applied, and recorded with a unique correlation identifier in the audit log.

### Leaver
When an employee departs the organization:
1. The identity status is immediately transitioned to disabled.
2. All assigned groups, application access entitlements, and granular permissions are revoked.
3. The offboarding action and timestamp are recorded in the audit trail to confirm access termination.

---

## Why JML Matters

Automated, auditable identity lifecycle management is a vital security discipline:

- **Prevents Stale Access**: Guarantees that departed personnel cannot retain active credentials or entitlements.
- **Mitigates Privilege Creep**: Systematically strips obsolete permissions when responsibilities change.
- **Enforces Least Privilege**: Baseline access profiles ensure personnel receive only what is necessary for their current function.
- **Reduces Operational Errors**: Eliminates manual checklist omissions and inconsistencies during onboarding and offboarding.
- **Strengthens Audit Readiness**: Provides compliance auditors with verifiable, end-to-end evidence of access changes.

---

## Role-Based Access Control (RBAC)

IAM ConCen replaces ad-hoc permission grants with a formal Role-Based Access Control (RBAC) model. Permissions are never assigned arbitrarily; instead, they are bound to predefined job roles.

```text
Employee
  → Department
  → Job Role
  → Groups / Enterprise Applications
  → Granular Permissions
  → AWS Cloud Roles & Policies
```

### Why RBAC?
- **Predictable Access**: Every employee in the same job role receives the identical baseline profile.
- **Simplified Auditing**: Access reviews assess whether an individual's assigned role matches their responsibilities, rather than evaluating hundreds of individual permissions manually.
- **Scalable Administration**: Updating permissions for a job role updates access expectations across all associated identities consistently.

---

## Least Privilege

The principle of least privilege dictates that an identity should possess only the minimum permissions necessary to perform its legitimate job functions—and nothing more.

### Example in Practice
- A **Finance Analyst** is granted access to the internal portal and the finance portal with read and approval permissions for financial records. They do not receive access to source code repositories, engineering issue trackers, or cloud infrastructure administration.
- A **Developer** receives access to source repositories, development tools, and scoped cloud development resources, but is excluded from financial systems and platform administrator rights.

IAM ConCen actively detects violations of least privilege, flagging identities that have accumulated permissions outside their authorized role catalog.

---

## Access Review

The **Access Review** engine provides continuous certification of user entitlements across the organization.

```text
Expected Access (Role Catalog)   vs   Actual Access (Assigned Profile)
                             ↓
             Variance & Findings Analysis
                             ↓
       [Compliant]  OR  [Privilege Creep / Excessive Access]
                             ↓
                    Remediation Workflow
```

Reviewers use this interface to examine:
- **Expected Access**: Entitlements prescribed by the authoritative role catalog.
- **Actual Access**: Entitlements currently attached to the employee's identity in the runtime store.
- **Excessive Access & Privilege Creep**: Retained permissions from prior positions or out-of-band assignments.
- **Privileged Identities**: Identities holding high-impact roles or sensitive administrative entitlements.
- **Risk-Rated Findings**: Issues classified with explicit risk levels (e.g., Critical, High, Medium, Low).
- **Remediation**: Reconciling the identity's profile by removing unapproved entitlements and restoring alignment with policy.

---

## Privileged Access

A privileged identity is an account holding permissions that allow administrative configuration, security policy alteration, or broad visibility across resources.

In IAM ConCen, privileged access is tracked deliberately:
- Privileged identities (such as platform administrators or roles accessing cloud console environments) are explicitly highlighted in the dashboard.
- Privileged access is neither inherently good nor bad—certain functions require elevated authority. The critical governance requirement is verifying that elevated access is justifiable, authorized, actively monitored, and granted only to those who require it.

---

## Security & Audit

The **Security & Audit** engine maintains an immutable record of identity events across the system, providing visibility into:

| Audit Attribute | Description |
|---|---|
| **Timestamp** | Local and UTC timestamp of the event |
| **Actor** | Identity or administrative role initiating the change |
| **Employee Target** | Identity profile affected by the action |
| **Activity** | Standardized action (e.g., onboarding, role adjustment, permission grant/revocation) |
| **Status** | Outcome of the operation (Successful, Failed, Denied) |
| **Correlation ID** | Unique tracking identifier linking related operations across transactions |

The audit engine tracks lifecycle changes, access reconciliations, and security findings, allowing administrators to inspect full state transitions (before and after snapshots) for any event.

---

## AWS Integration

IAM ConCen provides dedicated integration with Amazon Web Services, offering visibility into cloud IAM resources and access posture.

```text
                          ┌────────────────────────┐
                          │   BotoAwsConnector     │
                          │ (Read-Only STS Session)│
                          └───────────┬────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              │                       │                       │
              ▼                       ▼                       ▼
           AWS IAM                Amazon S3              AWS CloudTrail
      Roles & Policies        Allowlisted Buckets         Audit Activity
```

### AWS IAM
Inspects IAM roles, customer-managed policies, AWS-managed policies, and inline policies. It identifies trusted principals and role-policy bindings.

### IAM Roles & AWS STS
Connects using AWS Security Token Service (`sts:GetCallerIdentity`) to verify session context and account boundary without requiring persistent static administrator keys. Connections using AWS root credentials are expressly prohibited.

### Amazon S3
Validates accessibility for allowlisted, lab-scoped S3 buckets and object namespaces, demonstrating resource-level access governance.

### AWS CloudTrail
Ingests recent management and data events (`cloudtrail:LookupEvents`) to correlate cloud API actions with identity activity.

---

## Effective Access Evaluation

Determining effective access requires evaluating policies to discover whether an action will ultimately succeed or fail:

```text
      WHO?           Which IAM Role is requesting access?
       ↓
      WHAT?          Which AWS Resource (e.g., S3 Bucket / ARN)?
       ↓
  WHICH ACTION?      Which API operation (e.g., s3:GetObject, s3:PutObject)?
       ↓
      WHY?           Which policy statements match (Allow vs Explicit Deny)?
       ↓
    DECISION         ALLOWED  /  EXPLICIT DENY  /  NOT GRANTED  /  UNKNOWN
```

### Evaluation Logic
1. **Explicit Deny**: If any applicable policy statement contains an explicit `Deny`, the request is immediately denied.
2. **Conditional Statements**: If matching statements contain unsupported runtime conditions (e.g., IP boundaries or MFA conditions), the evaluator returns `UNKNOWN` to indicate external context is required.
3. **Allow Found**: If an applicable identity-policy `Allow` matches and no deny exists, access is determined as `ALLOWED`.
4. **Default Deny**: If no statement explicitly grants the action, the decision is `NOT GRANTED`.

---

## AWS Access Center

The **AWS Access** section in the dashboard provides a structured interface for exploring cloud security configuration:

- **Resources**: View all cloud resources currently in scope, categorized by resource type and AWS region.
- **Roles**: Inspect IAM roles, trust policies, and assigned privilege tiers.
- **Policies**: Examine policy statements, distinguishing between allow rules, deny rules, and affected actions.
- **Effective Access**: Interactively select any role, target resource, and API action to execute a simulated policy evaluation.
- **STS Identity**: Verify current caller identity, account ID, and session security context.
- **CloudTrail**: Review recent AWS API activity including event names, calling identities, and target resources.
- **AWS Operations**: Inspect a synchronized history of administrative sync actions and status results.

---

## Dashboard Overview

The Streamlit web dashboard is structured into seven distinct navigation views:

| View | Purpose |
|---|---|
| **📊 Dashboard** | Executive summary displaying employee counts, department breakdown, and system health status. |
| **👥 Employees & Roles** | Searchable employee registry with department filters, status views, and complete entitlement profiles. |
| **🔄 Join / Move / Leave** | Interactive lifecycle staging interface to preview, confirm, and execute Joiner, Mover, and Leaver actions. |
| **🔍 Access Review** | Access certification engine displaying expected vs. actual entitlements, risk-rated findings, and one-click remediation. |
| **🛡️ Security & Audit** | Unified audit trail displaying identity lifecycle events, control checks, and technical log inspection. |
| **☁️ AWS Access** | AWS governance center showing roles, policies, resource scopes, STS identity, CloudTrail logs, and effective access evaluation. |
| **📋 Access Matrix** | Master catalog mapping job roles to authorized groups, business applications, and specific permissions. |

---

## Access Matrix

The Access Matrix establishes the authoritative mapping of roles to organizational entitlements:

$$\text{Employee} \longrightarrow \text{Job Role} \longrightarrow \text{Directory Groups} \longrightarrow \text{Business Applications} \longrightarrow \text{Permissions}$$

This matrix serves as the single source of truth against which all access reviews and lifecycle transitions are evaluated.

---

## System Architecture

```text
                           ┌─────────────────────────┐
                           │   Streamlit Dashboard   │
                           │     (dashboard/app.py)  │
                           └────────────┬────────────┘
                                        │
           ┌────────────────────────────┼────────────────────────────┐
           ▼                            ▼                            ▼
   ┌───────────────┐            ┌───────────────┐            ┌───────────────┐
   │ Lifecycle     │            │ Access Review │            │ Security &    │
   │ Service (JML) │            │ Service       │            │ Audit Service │
   └───────┬───────┘            └───────┬───────┘            └───────┬───────┘
           │                            │                            │
           └────────────────────────────┼────────────────────────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │   Domain & Catalog Layer    │
                         │ (Roles, Policies, Entities) │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         ▼                             ▼
             ┌──────────────────────┐      ┌──────────────────────┐
             │ SQLite Local Store   │      │ AWS Boto Connector   │
             │ (Identity & Audit)   │      │ (Read-Only Lab APIs) │
             └──────────────────────┘      └───────────┬──────────┘
                                                       │
                                        ┌──────────────┼──────────────┐
                                        ▼              ▼              ▼
                                     AWS IAM        AWS STS       AWS CloudTrail
                                     & S3           Caller        Event Lookup
```

---

## Technology Stack

| Technology | Purpose | Implementation Details |
|---|---|---|
| **Python** | Core application logic | Python 3.11+, typed domain models, service architecture |
| **Streamlit** | Interactive UI | Multi-page layout, custom design system, light/dark mode support |
| **SQLite** | Runtime persistence | Local relational database for identities, assignments, and audit logs |
| **Boto3 (AWS SDK)** | AWS integration | Read-only connectors for IAM, STS, S3, and CloudTrail |
| **AWS IAM** | Cloud identity control | Role discovery, trust relationships, and policy evaluation |
| **AWS STS** | Identity verification | Non-root session authentication and caller identity validation |
| **Amazon S3** | Cloud resource target | Scoped, allowlisted bucket metadata inspection |
| **AWS CloudTrail** | Cloud audit telemetry | Ingestion of recent API events for identity correlation |
| **Pytest** | Automated test suite | Unit, integration, and policy evaluation testing |
| **Git / GitHub** | Version control | Source tracking and codebase governance |

---

## Project Structure

```text
IAM-ConCen/
│
├── dashboard/
│   └── app.py                  # Streamlit web dashboard application
│
├── src/
│   └── cilamp/                 # Core application package
│       ├── access_review_service.py  # Access review and remediation logic
│       ├── aws_policy.py             # AWS policy and effective access evaluation
│       ├── aws_repository.py         # SQLite persistence for cached AWS data
│       ├── aws_service.py            # AWS synchronization orchestration
│       ├── config.py                 # Application settings and environment parsing
│       ├── connectors/
│       │   └── aws/                  # Boto3 adapter and AWS models
│       ├── database.py               # SQLite connection and migration helpers
│       ├── domain.py                 # Core domain models and dataclasses
│       ├── iam_catalog.py            # Authoritative RBAC role and permission matrix
│       ├── lifecycle.py              # Pure JML planning functions
│       ├── lifecycle_service.py      # Lifecycle orchestration and validation
│       ├── repository.py             # Employee, access, and audit SQLite operations
│       ├── security.py               # Security scenario definitions and rules
│       └── security_service.py       # Security findings and case management
│
├── data/
│   └── cilamp.db               # Local runtime SQLite database
│
├── docs/                       # Architectural guides and documentation
│   ├── ARCHITECTURE.md         # Technical architecture documentation
│   ├── DECISIONS.md            # Architecture decision records (ADRs)
│   ├── DEMO_GUIDE.md           # Step-by-step presentation guide
│   ├── IAM_MODEL.md            # Detailed RBAC and access definitions
│   └── SECURITY_MODEL.md       # Security controls and threat modeling
│
├── tests/                      # Automated test suite
│   ├── test_access_review_integration.py
│   ├── test_aws_connector.py
│   ├── test_aws_integration.py
│   ├── test_aws_policy.py
│   ├── test_lifecycle.py
│   ├── test_lifecycle_integration.py
│   ├── test_security.py
│   └── ...
│
├── .env.example                # Sample environment configuration template
├── .gitignore                  # Git ignore definitions
├── pyproject.toml              # Build metadata, project dependencies, and tool config
├── requirements.txt            # Package dependencies
└── README.md                   # Project documentation
```

---

## Prerequisites

Before running the application, ensure the following are available on your system:

- **Python 3.11** or newer
- **Git**
- **Windows PowerShell** (or bash on Linux/macOS)
- *(Optional)* An **AWS Account** with configured credentials (via AWS CLI or environment variables) if running in live AWS mode. The application runs in full simulation mode by default without requiring an AWS account.

---

## Installation

Follow these steps to configure the local environment on Windows:

```powershell
# 1. Clone the repository
git clone https://github.com/aum2606/IAM-ConCen.git
cd IAM-ConCen

# 2. Create and activate a Python virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 3. Install dependencies in editable mode with development packages
python -m pip install -e ".[dev]"
```

---

## Running the Application

To launch the Streamlit dashboard:

```powershell
python -m streamlit run dashboard/app.py
```

Once initialized, Streamlit will display the local access URL:

```text
Local URL: http://localhost:8501
```

Open this address in any modern web browser to interact with the dashboard.

---

## Testing

The project includes an automated test suite verifying lifecycle transitions, access reviews, policy evaluation, and AWS connectors.

Run the test suite using:

```powershell
python -m pytest
```

The tests run with SQLite in-memory databases and mock AWS connectors, requiring no external network connectivity or cloud credentials.

---

## AWS Configuration

The application operates in **Simulation Mode** by default. To connect to an AWS lab account for read-only posture inspection:

1. Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
2. Configure your lab settings in `.env`:
   ```ini
   IAMCONCEN_MODE=LIVE_LAB
   IAMCONCEN_AWS_LAB_ENABLED=true
   IAMCONCEN_AWS_ACCOUNT_ID=123456789012
   IAMCONCEN_AWS_REGION=ap-south-1
   IAMCONCEN_AWS_PROFILE=default
   IAMCONCEN_AWS_ROLE_PATH=/iamconcen/
   IAMCONCEN_AWS_ALLOWED_BUCKETS=my-lab-bucket-name
   ```

### Security Safeguards
- **Never Commit Secrets**: Ensure `.env` and AWS credentials are never committed to version control.
- **Read-Only Scope**: The connector exposes no mutation methods (`Create`, `Delete`, `Update`, `Put`). It relies exclusively on read and list APIs.
- **Root Credentials Prohibited**: The application checks caller identity via STS and terminates immediately if root credentials are used.
- **Role Path & Account Scoping**: AWS inspection is bounded strictly to the designated account ID and role path prefix.

---

## Security Considerations

- **Least Privilege by Default**: Identity access baselines are mapped strictly to designated job functions.
- **Explicit Role-Based Boundaries**: Access outside the approved role catalog is detected and highlighted as a security finding.
- **Audit Immutability**: All identity lifecycle actions and access modifications generate correlated audit log entries.
- **Separation of Concerns**: Simulated organizational data is isolated from cloud infrastructure accounts.
- **Defensive AWS Connector Design**: In live mode, the AWS connector validates caller identity before making requests and operates in read-only capacity.

---

## Troubleshooting

### Streamlit Command Not Found
If running `streamlit run` indicates the command is not recognized, run it directly through Python within your activated virtual environment:
```powershell
python -m streamlit run dashboard/app.py
```

### Virtual Environment Activation Script Disabled
If Windows PowerShell prevents activating `.venv`, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

### Port Already in Use
If port 8501 is occupied by another application, launch Streamlit on an alternate port:
```powershell
python -m streamlit run dashboard/app.py --server.port 8502
```

### AWS Connection Fails
- Verify that your local AWS credentials are valid via `aws sts get-caller-identity`.
- Confirm that the account ID configured in `.env` matches the authenticated identity.
- Verify that your IAM identity has read permissions for IAM (`iam:ListRoles`, `iam:GetPolicy`), S3 (`s3:HeadBucket`), and CloudTrail (`cloudtrail:LookupEvents`).

---

## Example IAM Scenarios

### Scenario 1 — New Employee Onboarding (Joiner)
An engineer joins as a **Developer**. The Joiner workflow automatically provisions membership in `Developers`, access to Jira, GitHub, and internal tools, and scoped cloud development permissions, recording the action in the audit log.

### Scenario 2 — Department Transfer (Mover)
A Developer transitions into an **Engineering Manager**. The Mover workflow provisions management permissions, grants membership in `People Managers`, and identifies redundant development-only access for revocation.

### Scenario 3 — Employee Departure (Leaver)
An employee departs the organization. The Leaver workflow disables the identity record, strips all group memberships and application entitlements, and creates an audit record documenting complete access termination.

### Scenario 4 — Privilege Creep Remediation
An access review identifies a Developer holding unapproved `platform.administrator` rights. The finding is flagged as Critical. An administrator triggers reconciliation, revoking the excessive entitlement and restoring compliance.

### Scenario 5 — Effective AWS Policy Evaluation
An access evaluation is performed to determine if a Developer role can execute `s3:DeleteObject` on a production bucket. The engine analyzes attached policies, finds no allow statement, and returns an explainable `NOT GRANTED` decision.

---

## Project Goals

This project was developed to demonstrate practical competency across core cloud security and identity engineering disciplines:

- Implementing scalable **Role-Based Access Control (RBAC)**
- Automating **Joiner-Mover-Leaver (JML)** identity lifecycle operations
- Designing continuous **Access Certification** and remediation workflows
- Evaluating **AWS IAM Policies** and effective permissions
- Integrating **AWS STS, IAM, S3, and CloudTrail** telemetry
- Establishing secure audit tracking and governance controls
- Building intuitive, production-styled command centers for security operations

---

## Limitations

- **Portfolio & Demonstration Focus**: This project is built as an educational and portfolio system to demonstrate IAM principles and is not intended for direct enterprise production deployment.
- **Simulated Directory Data**: Organizational identity records are maintained within a local relational database rather than an enterprise identity provider like Okta, Ping, or Microsoft Entra ID.
- **Bounded AWS Evaluation**: The local effective access engine evaluates attached identity policies and explicit denies. It does not evaluate external dimensions such as Service Control Policies (SCPs), Permissions Boundaries, or live session policies.

---

## Future Improvements

- Integration with **AWS IAM Identity Center** (SSO) for centralized multi-account permission sets.
- Multi-step approval workflows for high-risk access requests.
- Webhook notifications for security findings via Slack or email.
- Automated generation of downloadable PDF compliance and access review reports.
- Extended CI/CD policy linting using tools like `cfn-lint` and `tfsec`.

---

## Project Status

**Active Portfolio Project** — Fully functional AWS-focused Cloud Identity & Access Management platform demonstrating identity lifecycle operations, RBAC governance, security auditing, and AWS IAM posture inspection.

---

## Author

**Panthil Shah**  
MSc IT

---

## License

This project is developed for educational, demonstration, and portfolio purposes.
