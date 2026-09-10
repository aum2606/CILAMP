from dataclasses import replace

from cilamp.azure_policy import evaluate_azure_access, scope_applies
from cilamp.connectors.azure.simulation import SimulationAzureConnector


def _snapshot():
    return SimulationAzureConnector().read_snapshot()


def test_scope_hierarchy_applies_to_children_but_not_siblings() -> None:
    snapshot = _snapshot()
    resource_group = snapshot.resources[0]
    dev_storage = next(item for item in snapshot.resources if item.name == "stcilampdev")
    archive = next(item for item in snapshot.resources if item.name == "stcilamparchive")

    assert scope_applies(resource_group.resource_id, dev_storage.resource_id)
    assert not scope_applies(dev_storage.resource_id, archive.resource_id)


def test_developer_has_narrow_blob_read_but_no_write_or_archive_access() -> None:
    snapshot = _snapshot()
    developer = next(item for item in snapshot.identities if item.display_name == "Developers")
    dev_storage = next(item for item in snapshot.resources if item.name == "stcilampdev")
    archive = next(item for item in snapshot.resources if item.name == "stcilamparchive")

    read = evaluate_azure_access(
        developer.principal_id,
        developer.display_name,
        dev_storage,
        "storage.blob.read",
        snapshot.role_assignments,
    )
    write = evaluate_azure_access(
        developer.principal_id,
        developer.display_name,
        dev_storage,
        "storage.blob.write",
        snapshot.role_assignments,
    )
    archive_read = evaluate_azure_access(
        developer.principal_id,
        developer.display_name,
        archive,
        "storage.blob.read",
        snapshot.role_assignments,
    )

    assert read.decision == "ALLOWED"
    assert read.matched_roles == ("Storage Blob Data Reader",)
    assert write.decision == "NOT GRANTED"
    assert archive_read.decision == "NOT GRANTED"


def test_managed_identity_can_read_required_data_but_cannot_manage_rbac() -> None:
    snapshot = _snapshot()
    identity = next(
        item for item in snapshot.identities if item.display_name == "reporting-api-mi"
    )
    vault = next(item for item in snapshot.resources if item.name == "kv-cilamp-lab")

    secret_read = evaluate_azure_access(
        identity.principal_id,
        identity.display_name,
        vault,
        "keyvault.secret.read",
        snapshot.role_assignments,
    )
    rbac = evaluate_azure_access(
        identity.principal_id,
        identity.display_name,
        vault,
        "rbac.manage",
        snapshot.role_assignments,
    )

    assert secret_read.decision == "ALLOWED"
    assert rbac.decision == "NOT GRANTED"
    assert identity.credential_mode == "MANAGED_IDENTITY_NO_STORED_SECRET"


def test_reader_management_role_does_not_grant_blob_data_access() -> None:
    snapshot = _snapshot()
    security = next(
        item for item in snapshot.identities if item.display_name == "Security Administrators"
    )
    storage = next(item for item in snapshot.resources if item.name == "stcilampdev")

    management_read = evaluate_azure_access(
        security.principal_id,
        security.display_name,
        storage,
        "resource.read",
        snapshot.role_assignments,
    )
    data_read = evaluate_azure_access(
        security.principal_id,
        security.display_name,
        storage,
        "storage.blob.read",
        snapshot.role_assignments,
    )

    assert management_read.decision == "ALLOWED"
    assert data_read.decision == "NOT GRANTED"


def test_unknown_or_conditional_role_does_not_create_false_denial() -> None:
    snapshot = _snapshot()
    developer = next(item for item in snapshot.identities if item.display_name == "Developers")
    storage = next(item for item in snapshot.resources if item.name == "stcilampdev")
    custom = replace(snapshot.role_assignments[0], role_name="Custom Data Role (CONDITIONAL)")

    decision = evaluate_azure_access(
        developer.principal_id,
        developer.display_name,
        storage,
        "storage.blob.write",
        (custom,),
    )

    assert decision.decision == "UNKNOWN"


def test_owner_management_role_does_not_imply_blob_data_access() -> None:
    snapshot = _snapshot()
    developer = next(item for item in snapshot.identities if item.display_name == "Developers")
    storage = next(item for item in snapshot.resources if item.name == "stcilampdev")
    owner = replace(snapshot.role_assignments[0], role_name="Owner")

    decision = evaluate_azure_access(
        developer.principal_id,
        developer.display_name,
        storage,
        "storage.blob.read",
        (owner,),
    )

    assert decision.decision == "NOT GRANTED"
