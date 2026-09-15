from pathlib import Path

import pytest

from cilamp.config import load_settings


def test_defaults_to_simulation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IAMCONCEN_MODE", raising=False)
    monkeypatch.delenv("CILAMP_MODE", raising=False)
    monkeypatch.delenv("IAMCONCEN_DATABASE_PATH", raising=False)
    monkeypatch.delenv("CILAMP_DATABASE_PATH", raising=False)

    settings = load_settings()

    assert settings.mode == "SIMULATION"
    assert settings.database_path.name == "cilamp.db"


def test_relative_database_path_is_resolved(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IAMCONCEN_DATABASE_PATH", "data/test.db")

    assert load_settings().database_path.is_absolute()


def test_live_mode_requires_explicit_lab_guard(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IAMCONCEN_MODE", "LIVE_LAB")
    monkeypatch.delenv("CILAMP_MODE", raising=False)
    monkeypatch.delenv("IAMCONCEN_AWS_LAB_ENABLED", raising=False)
    monkeypatch.delenv("CILAMP_AWS_LAB_ENABLED", raising=False)
    monkeypatch.delenv("IAMCONCEN_AWS_ACCOUNT_ID", raising=False)
    monkeypatch.delenv("CILAMP_AWS_ACCOUNT_ID", raising=False)

    with pytest.raises(ValueError, match="dedicated lab"):
        load_settings()


def test_aws_live_lab_uses_non_secret_scope_controls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("IAMCONCEN_MODE", "LIVE_LAB")
    monkeypatch.delenv("CILAMP_MODE", raising=False)
    monkeypatch.setenv("IAMCONCEN_AWS_LAB_ENABLED", "true")
    monkeypatch.delenv("CILAMP_AWS_LAB_ENABLED", raising=False)
    monkeypatch.setenv("IAMCONCEN_AWS_ACCOUNT_ID", "123456789012")
    monkeypatch.delenv("CILAMP_AWS_ACCOUNT_ID", raising=False)
    monkeypatch.setenv("IAMCONCEN_AWS_PROFILE", "iamconcen-lab-sso")
    monkeypatch.delenv("CILAMP_AWS_PROFILE", raising=False)
    monkeypatch.setenv("IAMCONCEN_AWS_ROLE_PATH", "/iamconcen/")
    monkeypatch.delenv("CILAMP_AWS_ROLE_PATH", raising=False)
    monkeypatch.setenv("IAMCONCEN_AWS_ALLOWED_BUCKETS", "iamconcen-dev, iamconcen-reports")
    monkeypatch.delenv("CILAMP_AWS_ALLOWED_BUCKETS", raising=False)

    settings = load_settings()

    assert settings.mode == "LIVE_LAB"
    assert settings.aws_lab_enabled
    assert settings.aws_account_id == "123456789012"
    assert settings.aws_profile == "iamconcen-lab-sso"
    assert settings.aws_allowed_buckets == ("iamconcen-dev", "iamconcen-reports")
