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


def test_phase_zero_rejects_live_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CILAMP_MODE", "LIVE_LAB")

    with pytest.raises(ValueError, match="SIMULATION mode only"):
        load_settings()
