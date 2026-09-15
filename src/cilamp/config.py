"""Safe local configuration for the IAM ConCen foundation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "data" / "cilamp.db"


@dataclass(frozen=True)
class Settings:
    """Runtime settings. Secret values are deliberately not represented here."""

    mode: str
    database_path: Path
    aws_lab_enabled: bool = False
    aws_account_id: str = ""
    aws_account_label: str = "Simulation AWS account"
    aws_region: str = "ap-south-1"
    aws_profile: str = ""
    aws_role_path: str = "/iamconcen/"
    aws_allowed_buckets: tuple[str, ...] = ()


def _database_path(raw_path: str | None) -> Path:
    if not raw_path:
        return DEFAULT_DATABASE_PATH

    configured = Path(raw_path).expanduser()
    return configured if configured.is_absolute() else PROJECT_ROOT / configured


def load_settings() -> Settings:
    """Load safe settings and require an explicit guard for live lab mode."""

    mode = os.getenv("IAMCONCEN_MODE", os.getenv("CILAMP_MODE", "SIMULATION")).strip().upper()
    if mode not in {"SIMULATION", "LIVE_LAB"}:
        raise ValueError("IAMCONCEN_MODE must be SIMULATION or LIVE_LAB.")

    aws_lab_enabled = os.getenv("IAMCONCEN_AWS_LAB_ENABLED", os.getenv("CILAMP_AWS_LAB_ENABLED", "false")).strip().lower() == "true"
    aws_account_id = os.getenv("IAMCONCEN_AWS_ACCOUNT_ID", os.getenv("CILAMP_AWS_ACCOUNT_ID", "")).strip()
    aws_ready = aws_lab_enabled and aws_account_id.isdigit() and len(aws_account_id) == 12
    if mode == "LIVE_LAB" and not aws_ready:
        raise ValueError(
            "LIVE_LAB requires an explicitly enabled AWS dedicated lab "
            "with a valid 12-digit account ID."
        )

    return Settings(
        mode=mode,
        database_path=_database_path(os.getenv("IAMCONCEN_DATABASE_PATH", os.getenv("CILAMP_DATABASE_PATH"))),
        aws_lab_enabled=aws_lab_enabled,
        aws_account_id=aws_account_id,
        aws_account_label=os.getenv("IAMCONCEN_AWS_ACCOUNT_LABEL", os.getenv("CILAMP_AWS_ACCOUNT_LABEL", "Simulation AWS account")).strip() or "Dedicated AWS lab",
        aws_region=os.getenv("IAMCONCEN_AWS_REGION", os.getenv("CILAMP_AWS_REGION", "ap-south-1")).strip() or "ap-south-1",
        aws_profile=os.getenv("IAMCONCEN_AWS_PROFILE", os.getenv("CILAMP_AWS_PROFILE", "")).strip(),
        aws_role_path=os.getenv("IAMCONCEN_AWS_ROLE_PATH", os.getenv("CILAMP_AWS_ROLE_PATH", "/iamconcen/")).strip() or "/iamconcen/",
        aws_allowed_buckets=tuple(item.strip() for item in os.getenv("IAMCONCEN_AWS_ALLOWED_BUCKETS", os.getenv("CILAMP_AWS_ALLOWED_BUCKETS", "")).split(",") if item.strip()),
    )
