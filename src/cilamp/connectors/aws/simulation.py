"""Deterministic least-privilege AWS IAM laboratory."""

from datetime import datetime, timezone

from cilamp.connectors.aws.models import AwsCloudTrailEvent, AwsPolicy, AwsPolicyStatement, AwsResource, AwsRole, AwsRolePolicyBinding, AwsSnapshot


ACCOUNT = "111122223333"
DEV_BUCKET = "arn:aws:s3:::cilamp-lab-development"
REPORT_BUCKET = "arn:aws:s3:::cilamp-lab-reports"


class SimulationAwsConnector:
    mode = "SIMULATION"

    def check_connection(self) -> str:
        return "SIMULATED"

    def read_snapshot(self) -> AwsSnapshot:
        roles = (
            AwsRole(f"arn:aws:iam::{ACCOUNT}:role/cilamp/CILAMP-DeveloperRole", "CILAMP-DeveloperRole", "/cilamp/", ("IAM Identity Center federated sessions",), "STS_TEMPORARY_CREDENTIALS"),
            AwsRole(f"arn:aws:iam::{ACCOUNT}:role/cilamp/CILAMP-ReportingWorkloadRole", "CILAMP-ReportingWorkloadRole", "/cilamp/", ("lambda.amazonaws.com",), "IAM_ROLE_STS_NO_STORED_KEYS"),
            AwsRole(f"arn:aws:iam::{ACCOUNT}:role/cilamp/CILAMP-SecurityAuditRole", "CILAMP-SecurityAuditRole", "/cilamp/", ("IAM Identity Center federated sessions",), "STS_TEMPORARY_CREDENTIALS"),
        )
        policies = (
            AwsPolicy(f"arn:aws:iam::{ACCOUNT}:policy/cilamp/CILAMP-DeveloperS3Read", "CILAMP-DeveloperS3Read", "CUSTOMER_MANAGED", (
                AwsPolicyStatement("ListDevelopmentBucket", "Allow", ("s3:ListBucket",), (DEV_BUCKET,)),
                AwsPolicyStatement("ReadDevelopmentObjects", "Allow", ("s3:GetObject",), (f"{DEV_BUCKET}/*",)),
                AwsPolicyStatement("PreventObjectDeletion", "Deny", ("s3:DeleteObject",), ("arn:aws:s3:::cilamp-lab-*/*",)),
            )),
            AwsPolicy(f"arn:aws:iam::{ACCOUNT}:policy/cilamp/CILAMP-ReportingRead", "CILAMP-ReportingRead", "CUSTOMER_MANAGED", (AwsPolicyStatement("ReadReports", "Allow", ("s3:GetObject",), (f"{REPORT_BUCKET}/published/*",)),)),
            AwsPolicy(f"arn:aws:iam::{ACCOUNT}:policy/cilamp/CILAMP-SecurityAudit", "CILAMP-SecurityAudit", "CUSTOMER_MANAGED", (AwsPolicyStatement("ReadAuditMetadata", "Allow", ("iam:Get*", "iam:List*", "cloudtrail:LookupEvents"), ("*",)),)),
        )
        bindings = tuple(AwsRolePolicyBinding(role.arn, policy.arn) for role, policy in zip(roles, policies))
        return AwsSnapshot(
            (
                AwsResource(DEV_BUCKET, "cilamp-lab-development", "S3 bucket", "global"),
                AwsResource(f"{DEV_BUCKET}/onboarding-guide.pdf", "onboarding-guide.pdf", "S3 object", "global"),
                AwsResource(REPORT_BUCKET, "cilamp-lab-reports", "S3 bucket", "global"),
                AwsResource(f"{REPORT_BUCKET}/published/weekly.csv", "published/weekly.csv", "S3 object", "global"),
            ),
            roles, policies, bindings,
            (AwsCloudTrailEvent("sim-event-1", datetime(2026, 9, 10, 8, 30, tzinfo=timezone.utc), "AssumeRole", "developer@example.test", "CILAMP-DeveloperRole"), AwsCloudTrailEvent("sim-event-2", datetime(2026, 9, 10, 8, 35, tzinfo=timezone.utc), "GetObject", "CILAMP-DeveloperRole", "onboarding-guide.pdf")),
            f"arn:aws:sts::{ACCOUNT}:assumed-role/CILAMP-AuditDiscovery/cilamp",
            ("This teaching evaluator covers cached identity policies only; resource policies, SCPs/RCPs, permissions boundaries, session policies, tags, and request context require AWS evaluation.",),
        )
