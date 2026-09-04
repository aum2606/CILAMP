from cilamp.project_status import CURRENT_PHASE, MODULE_STATUSES


def test_phase_two_status_matches_approved_scope() -> None:
    statuses = {item.module: item.status for item in MODULE_STATUSES}

    assert CURRENT_PHASE == "Phase 2 — Joiner-Mover-Leaver Engine"
    assert statuses["Organization Model"] == "Complete"
    assert statuses["JML Engine"] == "Complete"
    assert statuses["RBAC"] == "Not Started"
    assert statuses["Entra ID"] == "Not Connected"
    assert statuses["Azure"] == "Not Connected"
    assert statuses["AWS"] == "Not Connected"
