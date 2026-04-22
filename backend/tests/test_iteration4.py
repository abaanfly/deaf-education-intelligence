"""Iteration 4 tests — X-Admin-Token guard on /api/admin/open-dataset/*.

Verifies that:
  - Missing header => 401
  - Wrong header => 401
  - Correct header => 200 with normal payload
  - Idempotency still holds with correct token
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://deaf-learn-ai.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "deis-demo-admin-2026")
ADMIN_HEADERS = {"X-Admin-Token": ADMIN_TOKEN}


@pytest.fixture(scope="session")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


@pytest.fixture(scope="module", autouse=True)
def _reset_before_after(s):
    s.post(f"{API}/admin/open-dataset/reset", headers=ADMIN_HEADERS, timeout=20)
    yield
    s.post(f"{API}/admin/open-dataset/reset", headers=ADMIN_HEADERS, timeout=20)


# -------- 401 paths --------
@pytest.mark.parametrize(
    "method,path",
    [
        ("GET",  "/admin/open-dataset/info"),
        ("POST", "/admin/open-dataset/import"),
        ("POST", "/admin/open-dataset/reset"),
    ],
)
def test_admin_endpoint_requires_header(s, method, path):
    r = s.request(method, f"{API}{path}", timeout=15)
    assert r.status_code == 401, f"{method} {path} expected 401 without header, got {r.status_code}"
    body = r.json()
    assert body.get("detail") == "Invalid admin token"


@pytest.mark.parametrize(
    "method,path",
    [
        ("GET",  "/admin/open-dataset/info"),
        ("POST", "/admin/open-dataset/import"),
        ("POST", "/admin/open-dataset/reset"),
    ],
)
def test_admin_endpoint_rejects_wrong_token(s, method, path):
    r = s.request(method, f"{API}{path}", headers={"X-Admin-Token": "wrong-token"}, timeout=15)
    assert r.status_code == 401
    assert r.json().get("detail") == "Invalid admin token"


# -------- 200 with correct header --------
def test_admin_info_with_correct_token(s):
    r = s.get(f"{API}/admin/open-dataset/info", headers=ADMIN_HEADERS, timeout=15)
    assert r.status_code == 200
    data = r.json()
    for k in ("name", "source", "available_records", "already_imported"):
        assert k in data
    assert data["available_records"] == 30


def test_admin_import_idempotent_with_correct_token(s):
    # ensure clean state
    s.post(f"{API}/admin/open-dataset/reset", headers=ADMIN_HEADERS, timeout=20)

    r1 = s.post(f"{API}/admin/open-dataset/import", headers=ADMIN_HEADERS, timeout=60)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["imported_students"] == 30
    assert d1["already_existed"] == 0

    r2 = s.post(f"{API}/admin/open-dataset/import", headers=ADMIN_HEADERS, timeout=30)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["imported_students"] == 0
    assert d2["already_existed"] == 30


def test_admin_reset_with_correct_token(s):
    r = s.post(f"{API}/admin/open-dataset/reset", headers=ADMIN_HEADERS, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert "deleted_students" in data
    assert "deleted_attempts" in data


# -------- Negative: non-admin endpoints must NOT require the header --------
def test_non_admin_endpoint_unaffected(s):
    r = s.get(f"{API}/students", timeout=20)
    assert r.status_code == 200
