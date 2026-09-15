from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_dashboard_renders_without_exceptions(monkeypatch) -> None:
    database_path = Path(__file__).parents[1] / "data" / "test-dashboard.db"
    database_path.unlink(missing_ok=True)
    monkeypatch.setenv("IAMCONCEN_MODE", "SIMULATION")
    monkeypatch.setenv("IAMCONCEN_DATABASE_PATH", str(database_path))
    app_path = Path(__file__).parents[1] / "dashboard" / "app.py"

    try:
        dashboard = AppTest.from_file(str(app_path)).run(timeout=20)

        assert not dashboard.exception
        assert dashboard.markdown
        assert any(metric.value == "500" for metric in dashboard.metric)

        next(item for item in dashboard.radio if item.label == "Navigation").set_value(
            "👥 Employees & Roles"
        ).run(timeout=20)
        assert not dashboard.exception
        assert any(metric.label == "Matching Employees" for metric in dashboard.metric)

        next(item for item in dashboard.radio if item.label == "Navigation").set_value(
            "🔄 Join / Move / Leave"
        ).run(timeout=20)
        assert not dashboard.exception
        assert len(dashboard.tabs) == 4

        next(item for item in dashboard.radio if item.label == "Navigation").set_value(
            "🔍 Access Review"
        ).run(timeout=30)
        assert not dashboard.exception
        assert any(metric.label == "Reviewed Identities" for metric in dashboard.metric)
        assert any(metric.value == "500" for metric in dashboard.metric)

        next(item for item in dashboard.radio if item.label == "Navigation").set_value(
            "🛡️ Security & Audit"
        ).run(timeout=30)
        assert not dashboard.exception
        assert any(metric.label == "Total Audit Events" for metric in dashboard.metric)

        next(item for item in dashboard.radio if item.label == "Navigation").set_value(
            "☁️ AWS Access"
        ).run(timeout=30)
        assert not dashboard.exception
        assert any(metric.label == "AWS Connection" for metric in dashboard.metric)
        next(
            button
            for button in dashboard.button
            if button.label == "Synchronize AWS IAM"
        ).click().run(timeout=30)
        assert not dashboard.exception
        assert any(
            metric.label == "IAM Roles" and metric.value == "3"
            for metric in dashboard.metric
        )

        next(item for item in dashboard.radio if item.label == "Navigation").set_value(
            "📋 Access Matrix"
        ).run(timeout=20)
        assert not dashboard.exception
        assert len(dashboard.tabs) == 4
    finally:
        database_path.unlink(missing_ok=True)
