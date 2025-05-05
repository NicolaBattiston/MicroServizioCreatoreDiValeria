import pytest
import uuid
import requests

BASE_URL = "http://localhost:5000/api"
VALID_TOKEN = "valid-token-placeholder"
INVALID_TOKEN = "bad-token"

@pytest.fixture
def headers_valid():
    return {"Authorization": f"Next-Out {VALID_TOKEN}", "Content-Type": "application/json"}

@pytest.fixture
def headers_invalid():
    return {"Authorization": f"Next-Out {INVALID_TOKEN}", "Content-Type": "application/json"}

def test_start_with_valid_token(headers_valid):
    job_id = str(uuid.uuid4())
    resp = requests.post(f"{BASE_URL}/start", headers=headers_valid, json={"job_id": job_id})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "started"
    assert data.get("job_id") == job_id
    assert "link" in data

def test_start_without_token():
    job_id = str(uuid.uuid4())
    resp = requests.post(f"{BASE_URL}/start", json={"job_id": job_id})
    assert resp.status_code == 401

def test_start_with_invalid_token(headers_invalid):
    job_id = str(uuid.uuid4())
    resp = requests.post(f"{BASE_URL}/start", headers=headers_invalid, json={"job_id": job_id})
    assert resp.status_code == 401
