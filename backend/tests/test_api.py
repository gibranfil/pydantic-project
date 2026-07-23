from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_and_profile_endpoints_return_dto():
    response = client.post(
        "/upload",
        files={"file": ("sales.csv", b"Revenue,Profit,Region\n10,2,East\n20,4,West\n", "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["dataset"] == "sales.csv"
    assert body["profile"]["filename"] == "sales.csv"
    assert body["profile"]["rows"] == 2
    assert body["profile"]["columns"] == 3


def test_chat_endpoint_returns_response_model():
    response = client.post(
        "/chat",
        json={"message": "Summarize this dataset", "dataset": "sales.csv"},
    )

    assert response.status_code == 200
    body = response.json()

    assert "answer" in body
    assert isinstance(body["execution_time"], float)


def test_chat_endpoint_passes_dependencies_to_agent(monkeypatch):
    class FakeOutput:
        answer = "ok"

    class FakeResult:
        output = FakeOutput()

    async def fake_run(*args, **kwargs):
        assert "deps" in kwargs
        assert kwargs["deps"].dataset_manager is not None
        return FakeResult()

    mock_run = AsyncMock(side_effect=fake_run)
    monkeypatch.setattr("app.main.agent.run", mock_run)

    response = client.post(
        "/chat",
        json={"message": "Summarize this dataset", "dataset": "sales.csv"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "ok"


def test_chat_endpoint_returns_chart_url_when_agent_creates_chart(tmp_path, monkeypatch):
    chart_path = tmp_path / "sales_revenue_bar.png"
    chart_path.write_bytes(b"png")

    class FakeOutput:
        answer = "Chart created"

    class FakeResult:
        output = FakeOutput()

    async def fake_run(*args, **kwargs):
        kwargs["deps"].last_chart_path = str(chart_path)
        return FakeResult()

    monkeypatch.setattr("app.main.agent.run", AsyncMock(side_effect=fake_run))

    response = client.post(
        "/chat",
        json={"message": "Make a chart", "dataset": "sales.csv"},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Chart created"
    assert response.json()["chart_url"].endswith("/sales_revenue_bar.png")
