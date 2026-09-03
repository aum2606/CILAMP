"""Safe local configuration for the CILAMP foundation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "cilamp.db"


@dataclass(frozen=True)
class Settings:
    """Runtime settings that are safe to display in the Phase 0 dashboard."""

    mode: str
    database_path: Path


def _database_path(raw_path: str | None) -> Path:
    if not raw_path:
        return DEFAULT_DATABASE_PATH

    configured = Path(raw_path).expanduser()
    return configured if configured.is_absolute() else PROJECT_ROOT / configured


def load_settings() -> Settings:
    """Load Phase 0 settings and reject unsupported live execution."""

    mode = os.getenv("CILAMP_MODE", "SIMULATION").strip().upper()
    if mode != "SIMULATION":
        raise ValueError(
            "Phase 0 supports SIMULATION mode only. Live lab mode requires a later "
            "approved integration phase."
        )

    return Settings(
        mode=mode,
        database_path=_database_path(os.getenv("CILAMP_DATABASE_PATH")),
    )
