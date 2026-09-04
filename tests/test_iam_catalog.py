from cilamp.iam_catalog import (
    APPLICATIONS,
    DEPARTMENT_NAMES,
    GROUP_NAMES,
    PERMISSIONS,
    ROLES,
    ROLE_BY_NAME,
)


def test_catalog_objects_are_unique_and_roles_are_department_compatible() -> None:
    assert len(DEPARTMENT_NAMES) == len(set(DEPARTMENT_NAMES)) == 6
    assert len(ROLES) == len({role.name for role in ROLES}) == 10
    assert len(APPLICATIONS) == len({item.name for item in APPLICATIONS})
    assert len(PERMISSIONS) == len({item.name for item in PERMISSIONS})
    assert len(GROUP_NAMES) == len(set(GROUP_NAMES))
    assert all(role.department in DEPARTMENT_NAMES for role in ROLES)


def test_developer_receives_expected_but_not_unrelated_access() -> None:
    developer = ROLE_BY_NAME["Developer"]

    assert "GitHub" in developer.applications
    assert "Jira" in developer.applications
    assert "cloud.dev.read" in developer.permissions
    assert "Finance Portal" not in developer.applications
    assert "HR Portal" not in developer.applications
    assert "finance.approve" not in developer.permissions
    assert "cloud.ops.scoped" not in developer.permissions


def test_normal_business_roles_do_not_receive_cloud_administration() -> None:
    normal_roles = [role for role in ROLES if not role.privileged]

    assert all("cloud.ops.scoped" not in role.permissions for role in normal_roles)
