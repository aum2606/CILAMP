from cilamp.project_status import CURRENT_PHASE, MODULE_STATUSES


def test_phase_zero_status_matches_approved_scope() -> None:
    statuses = {item.module: item.status for item in MODULE_STATUSES}

    assert CURRENT_PHASE == "Phase 0 — Foundation"
    assert statuses["Organization Model"] == "Not Started"
    assert statuses["Entra ID"] == "Not Connected"
    assert statuses["Azure"] == "Not Connected"
    assert statuses["AWS"] == "Not Connected"
