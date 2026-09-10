from pathlib import Path

import pytest

from cilamp.config import load_settings


def test_defaults_to_simulation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CILAMP_MODE", raising=False)
    monkeypatch.delenv("CILAMP_DATABASE_PATH", raising=False)

    settings = load_settings()

    assert settings.mode == "SIMULATION"
    assert settings.database_path.name == "cilamp.db"


def test_relative_database_path_is_resolved(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CILAMP_DATABASE_PATH", "data/test.db")

    assert load_settings().database_path.is_absolute()


def test_live_mode_requires_explicit_lab_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CILAMP_MODE", "LIVE_LAB")
    monkeypatch.delenv("CILAMP_ENTRA_LAB_ENABLED", raising=False)
    monkeypatch.delenv("CILAMP_ENTRA_TENANT_ID", raising=False)

    with pytest.raises(ValueError, match="dedicated lab"):
        load_settings()


def test_live_mode_loads_non_secret_safety_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CILAMP_MODE", "LIVE_LAB")
    monkeypatch.setenv("CILAMP_ENTRA_LAB_ENABLED", "true")
    monkeypatch.setenv("CILAMP_ENTRA_TENANT_ID", "tenant-lab")
    monkeypatch.setenv("CILAMP_ENTRA_WRITES_ENABLED", "true")
    monkeypatch.setenv("CILAMP_ENTRA_ALLOWED_USER_DOMAIN", "lab.example")
    monkeypatch.setenv("CILAMP_ENTRA_ALLOWED_GROUP_IDS", "group-1, group-2")

    settings = load_settings()

    assert settings.mode == "LIVE_LAB"
    assert settings.entra_lab_enabled
    assert settings.entra_writes_enabled
    assert settings.entra_allowed_user_domain == "lab.example"
    assert settings.entra_allowed_group_ids == ("group-1", "group-2")


def test_azure_only_live_lab_requires_subscription_and_keeps_entra_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CILAMP_MODE", "LIVE_LAB")
    monkeypatch.setenv("CILAMP_ENTRA_LAB_ENABLED", "false")
    monkeypatch.delenv("CILAMP_ENTRA_TENANT_ID", raising=False)
    monkeypatch.setenv("CILAMP_AZURE_LAB_ENABLED", "true")
    monkeypatch.setenv("CILAMP_AZURE_TENANT_ID", "azure-lab-tenant")
    monkeypatch.setenv("CILAMP_AZURE_SUBSCRIPTION_ID", "azure-lab-subscription")
    monkeypatch.setenv("CILAMP_AZURE_RESOURCE_GROUP", "rg-cilamp-test")

    settings = load_settings()

    assert settings.mode == "LIVE_LAB"
    assert settings.azure_lab_enabled
    assert settings.azure_tenant_id == "azure-lab-tenant"
    assert settings.azure_subscription_id == "azure-lab-subscription"
    assert settings.azure_resource_group == "rg-cilamp-test"
    assert not settings.entra_lab_enabled


def test_aws_only_live_lab_uses_non_secret_scope_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CILAMP_MODE", "LIVE_LAB")
    monkeypatch.setenv("CILAMP_ENTRA_LAB_ENABLED", "false")
    monkeypatch.delenv("CILAMP_ENTRA_TENANT_ID", raising=False)
    monkeypatch.setenv("CILAMP_AWS_LAB_ENABLED", "true")
    monkeypatch.setenv("CILAMP_AWS_ACCOUNT_ID", "123456789012")
    monkeypatch.setenv("CILAMP_AWS_PROFILE", "cilamp-lab-sso")
    monkeypatch.setenv("CILAMP_AWS_ROLE_PATH", "/cilamp/")
    monkeypatch.setenv("CILAMP_AWS_ALLOWED_BUCKETS", "cilamp-dev, cilamp-reports")

    settings = load_settings()

    assert settings.aws_lab_enabled
    assert settings.aws_profile == "cilamp-lab-sso"
    assert settings.aws_allowed_buckets == ("cilamp-dev", "cilamp-reports")
