from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_renders_without_exceptions(monkeypatch) -> None:
    database_path = Path(__file__).parents[1] / "data" / "test-dashboard.db"
    database_path.unlink(missing_ok=True)
    monkeypatch.setenv("CILAMP_MODE", "SIMULATION")
    monkeypatch.setenv("CILAMP_DATABASE_PATH", str(database_path))
    app_path = Path(__file__).parents[1] / "dashboard" / "app.py"

    try:
        dashboard = AppTest.from_file(str(app_path)).run(timeout=20)

        assert not dashboard.exception
        assert dashboard.markdown
    finally:
        database_path.unlink(missing_ok=True)
