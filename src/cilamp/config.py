"""Safe local configuration for the CILAMP foundation."""

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
    entra_lab_enabled: bool = False
    entra_tenant_id: str = ""
    entra_tenant_label: str = "Simulation tenant"
    entra_auth_method: str = "AZURE_CLI"
    entra_writes_enabled: bool = False
    entra_allowed_user_domain: str = ""
    entra_allowed_group_ids: tuple[str, ...] = ()
    azure_lab_enabled: bool = False
    azure_tenant_id: str = ""
    azure_subscription_id: str = ""
    azure_subscription_label: str = "Simulation subscription"
    azure_resource_group: str = "rg-cilamp-lab"
    azure_auth_method: str = "AZURE_CLI"


def _database_path(raw_path: str | None) -> Path:
    if not raw_path:
        return DEFAULT_DATABASE_PATH

    configured = Path(raw_path).expanduser()
    return configured if configured.is_absolute() else PROJECT_ROOT / configured


def load_settings() -> Settings:
    """Load safe settings and require an explicit guard for live lab mode."""

    mode = os.getenv("CILAMP_MODE", "SIMULATION").strip().upper()
    if mode not in {"SIMULATION", "LIVE_LAB"}:
        raise ValueError("CILAMP_MODE must be SIMULATION or LIVE_LAB.")

    lab_enabled = os.getenv("CILAMP_ENTRA_LAB_ENABLED", "false").strip().lower() == "true"
    tenant_id = os.getenv("CILAMP_ENTRA_TENANT_ID", "").strip()
    azure_lab_enabled = (
        os.getenv("CILAMP_AZURE_LAB_ENABLED", "false").strip().lower() == "true"
    )
    azure_tenant_id = os.getenv("CILAMP_AZURE_TENANT_ID", tenant_id).strip()
    azure_subscription_id = os.getenv("CILAMP_AZURE_SUBSCRIPTION_ID", "").strip()
    entra_ready = lab_enabled and bool(tenant_id)
    azure_ready = azure_lab_enabled and bool(azure_tenant_id and azure_subscription_id)
    if mode == "LIVE_LAB" and not (entra_ready or azure_ready):
        raise ValueError(
            "LIVE_LAB requires an explicitly enabled Entra or Azure dedicated lab "
            "with its tenant and subscription identifiers."
        )

    auth_method = os.getenv("CILAMP_ENTRA_AUTH_METHOD", "AZURE_CLI").strip().upper()
    if auth_method not in {"AZURE_CLI", "DEFAULT"}:
        raise ValueError("CILAMP_ENTRA_AUTH_METHOD must be AZURE_CLI or DEFAULT.")
    azure_auth_method = os.getenv(
        "CILAMP_AZURE_AUTH_METHOD", auth_method
    ).strip().upper()
    if azure_auth_method not in {"AZURE_CLI", "DEFAULT"}:
        raise ValueError("CILAMP_AZURE_AUTH_METHOD must be AZURE_CLI or DEFAULT.")

    allowed_group_ids = tuple(
        item.strip()
        for item in os.getenv("CILAMP_ENTRA_ALLOWED_GROUP_IDS", "").split(",")
        if item.strip()
    )

    return Settings(
        mode=mode,
        database_path=_database_path(os.getenv("CILAMP_DATABASE_PATH")),
        entra_lab_enabled=lab_enabled,
        entra_tenant_id=tenant_id,
        entra_tenant_label=os.getenv(
            "CILAMP_ENTRA_TENANT_LABEL", "Simulation tenant"
        ).strip()
        or "Dedicated lab",
        entra_auth_method=auth_method,
        entra_writes_enabled=(
            os.getenv("CILAMP_ENTRA_WRITES_ENABLED", "false").strip().lower()
            == "true"
        ),
        entra_allowed_user_domain=os.getenv(
            "CILAMP_ENTRA_ALLOWED_USER_DOMAIN", ""
        ).strip().lower(),
        entra_allowed_group_ids=allowed_group_ids,
        azure_lab_enabled=azure_lab_enabled,
        azure_tenant_id=azure_tenant_id,
        azure_subscription_id=azure_subscription_id,
        azure_subscription_label=os.getenv(
            "CILAMP_AZURE_SUBSCRIPTION_LABEL", "Simulation subscription"
        ).strip()
        or "Dedicated lab subscription",
        azure_resource_group=os.getenv(
            "CILAMP_AZURE_RESOURCE_GROUP", "rg-cilamp-lab"
        ).strip()
        or "rg-cilamp-lab",
        azure_auth_method=azure_auth_method,
    )
