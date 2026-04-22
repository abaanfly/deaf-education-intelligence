"""Iteration 3 tests — CSV/PDF exports, encouragements, UCI dataset import."""
import os
import time
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
def _baseline_clean(s):
    """Ensure UCI dataset is reset before tests run so import counts are deterministic."""
    s.post(f"{API}/admin/open-dataset/reset", headers=ADMIN_HEADERS, timeout=20)
    yield
    # final cleanup after module
    s.post(f"{API}/admin/open-dataset/reset", headers=ADMIN_HEADERS, timeout=20)


# -------- CSV export --------
def test_export_csv(s):
    r = s.get(f"{API}/teacher/export/csv", timeout=30)
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("text/csv")
    text = r.text
    lines = [ln for ln in text.splitlines() if ln.strip()]
    assert lines[0].startswith("Student ID,Name,Grade,Avg Score %,Risk")
    # 10 baseline students after reset
    assert len(lines) - 1 == 10, f"expected 10 data rows, got {len(lines)-1}"


# -------- PDF export --------
def test_export_pdf(s):
    r = s.get(f"{API}/teacher/export/pdf", timeout=30)
    assert r.status_code == 200
    assert r.headers.get("content-type", "").startswith("application/pdf")
    assert r.content[:4] == b"%PDF"


# -------- Encouragements --------
def test_encouragement_create_and_list(s):
    payload = {"note": "celebrate progress"}
    r = s.post(f"{API}/students/stu_001/encouragement", json=payload, timeout=45)
    assert r.status_code == 200
    data = r.json()
    for k in ("id", "student_id", "student_name", "message", "teacher_note", "created_at"):
        assert k in data, f"missing {k}"
    assert data["student_id"] == "stu_001"
    assert isinstance(data["message"], str) and 0 < len(data["message"]) < 400
    assert data["teacher_note"] == "celebrate progress"

    # second call
    r2 = s.post(f"{API}/students/stu_001/encouragement", json={"note": "be specific"}, timeout=45)
    assert r2.status_code == 200

    time.sleep(0.5)
    r3 = s.get(f"{API}/students/stu_001/encouragements", timeout=15)
    assert r3.status_code == 200
    arr = r3.json()
    assert isinstance(arr, list) and len(arr) >= 2
    # newest first
    times = [m["created_at"] for m in arr]
    assert times == sorted(times, reverse=True)


def test_encouragement_404(s):
    r = s.post(f"{API}/students/nonexistent/encouragement", json={"note": "x"}, timeout=15)
    assert r.status_code == 404


# -------- Open dataset --------
def test_dataset_info(s):
    r = s.get(f"{API}/admin/open-dataset/info", headers=ADMIN_HEADERS, timeout=15)
    assert r.status_code == 200
    data = r.json()
    for k in ("name", "source", "available_records", "already_imported"):
        assert k in data
    assert data["available_records"] == 30
    assert data["already_imported"] == 0  # baseline reset


def test_dataset_import_then_idempotent(s):
    # First import
    r = s.post(f"{API}/admin/open-dataset/import", headers=ADMIN_HEADERS, timeout=60)
    assert r.status_code == 200
    data = r.json()
    assert data["imported_students"] == 30
    assert data["imported_attempts"] == 540
    assert data["already_existed"] == 0

    # /api/students reflects total
    r2 = s.get(f"{API}/students", timeout=30)
    assert r2.status_code == 200
    assert len(r2.json()) == 40

    # class overview reflects total
    r3 = s.get(f"{API}/teacher/class-overview", timeout=30)
    assert r3.status_code == 200
    assert r3.json()["total_students"] == 40

    # Second call - idempotent
    r4 = s.post(f"{API}/admin/open-dataset/import", headers=ADMIN_HEADERS, timeout=30)
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["imported_students"] == 0
    assert d4["already_existed"] == 30

    # info now shows already_imported
    r5 = s.get(f"{API}/admin/open-dataset/info", headers=ADMIN_HEADERS, timeout=15)
    assert r5.json()["already_imported"] == 30


def test_dataset_reset(s):
    # ensure imported (in case run alone)
    s.post(f"{API}/admin/open-dataset/import", headers=ADMIN_HEADERS, timeout=60)
    r = s.post(f"{API}/admin/open-dataset/reset", headers=ADMIN_HEADERS, timeout=30)
    assert r.status_code == 200
    data = r.json()
    assert data["deleted_students"] == 30
    assert data["deleted_attempts"] == 540

    # baseline restored
    r2 = s.get(f"{API}/students", timeout=20)
    assert len(r2.json()) == 10
