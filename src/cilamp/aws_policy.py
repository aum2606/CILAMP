"""Explainable, deliberately conservative AWS identity-policy evaluator."""

from fnmatch import fnmatchcase

from cilamp.connectors.aws.models import AwsAccessDecision, AwsPolicy, AwsResource, AwsRole, AwsRolePolicyBinding


ACTION_LABELS = {"s3:ListBucket": "List objects in an S3 bucket", "s3:GetObject": "Read an S3 object", "s3:PutObject": "Create or replace an S3 object", "s3:DeleteObject": "Delete an S3 object", "iam:CreateUser": "Create an IAM user", "iam:AttachRolePolicy": "Attach a policy to a role", "cloudtrail:LookupEvents": "Look up CloudTrail events"}


def evaluate_aws_access(role: AwsRole, resource: AwsResource, action: str, policies: list[AwsPolicy] | tuple[AwsPolicy, ...], bindings: list[AwsRolePolicyBinding] | tuple[AwsRolePolicyBinding, ...]) -> AwsAccessDecision:
    if action not in ACTION_LABELS:
        raise ValueError(f"Unsupported AWS action: {action}")
    policy_arns = {item.policy_arn for item in bindings if item.role_arn == role.arn}
    attached = [policy for policy in policies if policy.arn in policy_arns]
    matches = [(policy, statement) for policy in attached for statement in policy.statements if any(fnmatchcase(action.casefold(), pattern.casefold()) for pattern in statement.actions) and any(fnmatchcase(resource.arn, pattern) for pattern in statement.resources)]
    denies = sorted({policy.name for policy, statement in matches if statement.effect.casefold() == "deny" and not statement.has_conditions})
    if denies:
        return AwsAccessDecision(role.arn, role.name, resource.arn, resource.name, action, "EXPLICIT DENY", tuple(denies), f"An applicable Deny in {', '.join(denies)} overrides any Allow.")
    uncertain = sorted({policy.name for policy, statement in matches if statement.has_conditions})
    if uncertain:
        return AwsAccessDecision(role.arn, role.name, resource.arn, resource.name, action, "UNKNOWN", tuple(uncertain), "A matching conditional or unsupported statement needs the full AWS request context.")
    allows = sorted({policy.name for policy, statement in matches if statement.effect.casefold() == "allow"})
    if allows:
        return AwsAccessDecision(role.arn, role.name, resource.arn, resource.name, action, "ALLOWED", tuple(allows), f"An applicable identity-policy Allow was found in {', '.join(allows)}; external controls may still restrict live access.")
    return AwsAccessDecision(role.arn, role.name, resource.arn, resource.name, action, "NOT GRANTED", (), "No cached identity-policy statement grants this action on this resource.")
