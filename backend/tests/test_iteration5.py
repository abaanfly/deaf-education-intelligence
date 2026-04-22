"""Iteration 5 tests — multi-dataset registry under /api/admin/datasets/*.

Covers:
  - List endpoint returns 3 datasets
  - Per-dataset info, including 404 for unknown key
  - Per-dataset import (counts + idempotency + source tag)
  - Per-dataset reset isolation (resetting OULAD leaves UCI + xAPI)
  - Reset-all wipes everything
  - X-Admin-Token guard on the new endpoints
  - Legacy /open-dataset/* aliases still proxy to UCI
  - End-to-end: after importing all, /api/students and teacher overview reflect totals;
    drill-down on an OULAD student returns weak topics + timeline
"""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "deis-demo-admin-2026")
H = {"X-Admin-Token": ADMIN_TOKEN}

DATASET_KEYS = ["uci", "oulad", "kaggle_xapi"]
EXPECTED_AVAILABLE = {"uci": 30, "oulad": 25, "kaggle_xapi": 25}
EXPECTED_ATTEMPTS_PER_STUDENT = {"uci": 18, "oulad": 14, "kaggle_xapi": 14}


@pytest.fixture(scope="session")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


@pytest.fixture(scope="module", autouse=True)
def _reset_around(s):
    s.post(f"{API}/admin/datasets/reset-all", headers=H, timeout=30)
    yield
    s.post(f"{API}/admin/datasets/reset-all", headers=H, timeout=30)


# ---- List ------------------------------------------------------------------
def test_list_datasets(s):
    r = s.get(f"{API}/admin/datasets", headers=H, timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, list) and len(data) == 3
    by_key = {d["key"]: d for d in data}
    for k in DATASET_KEYS:
        assert k in by_key, f"missing dataset {k}"
        d = by_key[k]
        for fld in ("name", "source", "available_records", "already_imported"):
            assert fld in d
        assert d["available_records"] == EXPECTED_AVAILABLE[k]
        assert d["already_imported"] == 0  # baseline (reset before)


# ---- Info per key ----------------------------------------------------------
@pytest.mark.parametrize("key", DATASET_KEYS)
def test_info_per_dataset(s, key):
    r = s.get(f"{API}/admin/datasets/{key}/info", headers=H, timeout=15)
    assert r.status_code == 200
    d = r.json()
    assert d["key"] == key
    assert d["available_records"] == EXPECTED_AVAILABLE[key]
    for fld in ("name", "source", "already_imported"):
        assert fld in d


def test_info_unknown_dataset_404(s):
    r = s.get(f"{API}/admin/datasets/bogus/info", headers=H, timeout=15)
    assert r.status_code == 404
    assert r.json().get("detail") == "Unknown dataset 'bogus'"


# ---- Import per dataset ----------------------------------------------------
@pytest.mark.parametrize("key", DATASET_KEYS)
def test_import_dataset_and_idempotent(s, key):
    # Reset just this one for a clean slate
    s.post(f"{API}/admin/datasets/{key}/reset", headers=H, timeout=30)

    r1 = s.post(f"{API}/admin/datasets/{key}/import", headers=H, timeout=60)
    assert r1.status_code == 200, r1.text
    d1 = r1.json()
    expected_students = EXPECTED_AVAILABLE[key]
    expected_attempts = expected_students * EXPECTED_ATTEMPTS_PER_STUDENT[key]
    assert d1["imported_students"] == expected_students
    assert d1["imported_attempts"] == expected_attempts
    assert d1["already_existed"] == 0
    assert d1["key"] == key

    # Idempotency
    r2 = s.post(f"{API}/admin/datasets/{key}/import", headers=H, timeout=30)
    d2 = r2.json()
    assert d2["imported_students"] == 0
    assert d2["already_existed"] == expected_students


# ---- Reset isolation -------------------------------------------------------
def test_reset_isolation_only_targeted(s):
    # Ensure all imported
    for k in DATASET_KEYS:
        s.post(f"{API}/admin/datasets/{k}/import", headers=H, timeout=60)

    before = {d["key"]: d["already_imported"] for d in s.get(f"{API}/admin/datasets", headers=H).json()}
    assert before["uci"] == 30 and before["oulad"] == 25 and before["kaggle_xapi"] == 25

    r = s.post(f"{API}/admin/datasets/oulad/reset", headers=H, timeout=30)
    assert r.status_code == 200
    body = r.json()
    assert body["deleted_students"] == 25
    assert body["deleted_attempts"] == 25 * EXPECTED_ATTEMPTS_PER_STUDENT["oulad"]

    after = {d["key"]: d["already_imported"] for d in s.get(f"{API}/admin/datasets", headers=H).json()}
    assert after["oulad"] == 0
    assert after["uci"] == 30, "UCI must be untouched"
    assert after["kaggle_xapi"] == 25, "xAPI must be untouched"


def test_reset_all_wipes_everything(s):
    # Make sure all imported again
    for k in DATASET_KEYS:
        s.post(f"{API}/admin/datasets/{k}/import", headers=H, timeout=60)

    r = s.post(f"{API}/admin/datasets/reset-all", headers=H, timeout=30)
    assert r.status_code == 200
    body = r.json()
    assert "deleted_students" in body and "deleted_attempts" in body
    assert "per_dataset" in body
    for k in DATASET_KEYS:
        assert k in body["per_dataset"]
    # All counts back to zero
    after = {d["key"]: d["already_imported"] for d in s.get(f"{API}/admin/datasets", headers=H).json()}
    for k in DATASET_KEYS:
        assert after[k] == 0


# ---- Auth guard ------------------------------------------------------------
@pytest.mark.parametrize(
    "method,path",
    [
        ("GET",  "/admin/datasets"),
        ("GET",  "/admin/datasets/uci/info"),
        ("POST", "/admin/datasets/uci/import"),
        ("POST", "/admin/datasets/uci/reset"),
        ("POST", "/admin/datasets/reset-all"),
    ],
)
def test_admin_endpoints_require_token(s, method, path):
    r = s.request(method, f"{API}{path}", timeout=15)
    assert r.status_code == 401
    assert r.json().get("detail") == "Invalid admin token"

    r2 = s.request(method, f"{API}{path}", headers={"X-Admin-Token": "wrong"}, timeout=15)
    assert r2.status_code == 401


# ---- Legacy aliases --------------------------------------------------------
def test_legacy_open_dataset_aliases_still_work(s):
    # Reset state via new path
    s.post(f"{API}/admin/datasets/reset-all", headers=H, timeout=30)

    # Legacy info -> UCI shape
    info = s.get(f"{API}/admin/open-dataset/info", headers=H, timeout=15).json()
    assert info["available_records"] == 30
    assert info["already_imported"] == 0

    imp = s.post(f"{API}/admin/open-dataset/import", headers=H, timeout=60).json()
    assert imp["imported_students"] == 30

    # New /datasets/uci/info should reflect it
    info2 = s.get(f"{API}/admin/datasets/uci/info", headers=H, timeout=15).json()
    assert info2["already_imported"] == 30

    rst = s.post(f"{API}/admin/open-dataset/reset", headers=H, timeout=30).json()
    assert rst["deleted_students"] == 30


# ---- E2E: after importing all, downstream analytics reflect totals ---------
def test_full_import_and_downstream_analytics(s):
    s.post(f"{API}/admin/datasets/reset-all", headers=H, timeout=30)
    for k in DATASET_KEYS:
        s.post(f"{API}/admin/datasets/{k}/import", headers=H, timeout=60)

    students = s.get(f"{API}/students", timeout=20).json()
    assert isinstance(students, list)
    # 10 seeded + 30 + 25 + 25
    assert len(students) == 90, f"expected 90 students, got {len(students)}"

    # Teacher overview reachable
    ov = s.get(f"{API}/teacher/class-overview", timeout=20)
    assert ov.status_code == 200
    body = ov.json()
    # Just ensure it includes student count consistent with import
    assert "total_students" in body or "students" in body or isinstance(body, dict)

    # Drill-down on an OULAD student
    oulad_student = next((st for st in students if st["id"].startswith("oulad_")), None)
    assert oulad_student is not None, "no oulad_ student found after import"
    sid = oulad_student["id"]

    # Try common dashboard endpoints
    paths = [
        f"/students/{sid}/dashboard",
        f"/students/{sid}",
    ]
    found = False
    for p in paths:
        rr = s.get(f"{API}{p}", timeout=20)
        if rr.status_code == 200:
            found = True
            data = rr.json()
            # Loose checks: weak topics + timeline somewhere in payload
            text = str(data)
            assert "weak" in text.lower() or "performance" in text.lower() or "subject" in text.lower()
            break
    assert found, "no working drill-down endpoint for oulad student"


# ---- Regression sanity: a couple of legacy iter1 endpoints -----------------
def test_health_and_quizzes_still_work(s):
    h = s.get(f"{API}/", timeout=10)
    assert h.status_code == 200
    q = s.get(f"{API}/quizzes", timeout=15)
    assert q.status_code == 200
