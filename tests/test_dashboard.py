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
        assert any(metric.value == "500" for metric in dashboard.metric)

        next(item for item in dashboard.radio if item.label == "Navigate").set_value(
            "Organization Explorer"
        ).run(timeout=20)
        assert not dashboard.exception
        assert any(metric.label == "Matching employees" for metric in dashboard.metric)

        next(item for item in dashboard.radio if item.label == "Navigate").set_value(
            "JML Operations"
        ).run(timeout=20)
        assert not dashboard.exception
        assert len(dashboard.tabs) == 4

        next(item for item in dashboard.radio if item.label == "Navigate").set_value(
            "Access Review"
        ).run(timeout=30)
        assert not dashboard.exception
        assert any(metric.label == "Reviewed identities" for metric in dashboard.metric)
        assert any(metric.value == "500" for metric in dashboard.metric)

        next(item for item in dashboard.radio if item.label == "Navigate").set_value(
            "Security & Audit"
        ).run(timeout=30)
        assert not dashboard.exception
        assert len(dashboard.tabs) == 6
        assert any(metric.label == "Audit events" for metric in dashboard.metric)

        next(item for item in dashboard.radio if item.label == "Navigate").set_value(
            "Microsoft Entra"
        ).run(timeout=30)
        assert not dashboard.exception
        assert len(dashboard.tabs) == 6
        assert any(metric.label == "Connection" for metric in dashboard.metric)
        next(
            button
            for button in dashboard.button
            if button.label == "Synchronize Entra Directory"
        ).click().run(timeout=30)
        assert not dashboard.exception
        assert any(
            metric.label == "Cached users" and metric.value == "500"
            for metric in dashboard.metric
        )

        next(item for item in dashboard.radio if item.label == "Navigate").set_value(
            "Azure Access"
        ).run(timeout=30)
        assert not dashboard.exception
        assert len(dashboard.tabs) == 7
        assert any(metric.label == "Azure connection" for metric in dashboard.metric)
        next(
            button
            for button in dashboard.button
            if button.label == "Synchronize Azure RBAC"
        ).click().run(timeout=30)
        assert not dashboard.exception
        assert any(
            metric.label == "Resources in scope" and metric.value == "5"
            for metric in dashboard.metric
        )

        next(item for item in dashboard.radio if item.label == "Navigate").set_value(
            "Access Matrix"
        ).run(timeout=20)
        assert not dashboard.exception
        assert len(dashboard.tabs) == 4
    finally:
        database_path.unlink(missing_ok=True)
