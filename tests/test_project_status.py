from cilamp.project_status import CURRENT_PHASE, MODULE_STATUSES


def test_phase_one_status_matches_approved_scope() -> None:
    statuses = {item.module: item.status for item in MODULE_STATUSES}

    assert CURRENT_PHASE == "Phase 1 — Organization & IAM Model"
    assert statuses["Organization Model"] == "Complete"
    assert statuses["JML Engine"] == "Not Started"
    assert statuses["Entra ID"] == "Not Connected"
    assert statuses["Azure"] == "Not Connected"
    assert statuses["AWS"] == "Not Connected"
