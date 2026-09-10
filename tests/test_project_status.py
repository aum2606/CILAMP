from cilamp.project_status import CURRENT_PHASE, MODULE_STATUSES


def test_phase_six_status_matches_approved_scope() -> None:
    statuses = {item.module: item.status for item in MODULE_STATUSES}

    assert CURRENT_PHASE == "Phase 6 — Azure Identity & RBAC"
    assert statuses["Organization Model"] == "Complete"
    assert statuses["JML Engine"] == "Complete"
    assert statuses["RBAC"] == "Complete"
    assert statuses["Audit"] == "Complete"
    assert statuses["Entra ID"] == "Complete"
    assert statuses["Azure"] == "Complete"
    assert statuses["AWS"] == "Not Connected"
