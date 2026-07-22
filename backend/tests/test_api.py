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
