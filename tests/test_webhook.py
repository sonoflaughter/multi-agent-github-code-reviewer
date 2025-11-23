from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_request_review_endpoint():
    payload = {
        "type": "review_pr",
        "repo": "test/repo",
        "pr_number": 42,
        "requester": "alice@example.com",
        "instructions": "Focus on tests"
    }
    res = client.post("/v1/request-review", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "queued"
