"""DEIS backend API tests — covers students, quizzes, teacher, and AI tutor endpoints."""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://deaf-learn-ai.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="session")
def s():
    sess = requests.Session()
    sess.headers.update({"Content-Type": "application/json"})
    return sess


# -------- Health --------
def test_health(s):
    r = s.get(f"{API}/", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert data.get("service") == "DEIS"
    assert data.get("status") == "ok"


# -------- Students list --------
def test_list_students(s):
    r = s.get(f"{API}/students", timeout=20)
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list)
    assert len(arr) == 10
    sample = arr[0]
    for k in ("id", "name", "grade", "avatar", "avg_score", "risk", "weak_topics",
              "subject_scores", "weekly_progress", "total_attempts", "time_spent_min"):
        assert k in sample, f"missing key {k}"
    # No ObjectId leak
    for stu in arr:
        assert "_id" not in stu


def test_get_student(s):
    r = s.get(f"{API}/students/stu_001", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == "stu_001"
    assert "_id" not in data
    assert "avg_score" in data
    assert "subject_scores" in data


def test_get_student_404(s):
    r = s.get(f"{API}/students/nonexistent", timeout=15)
    assert r.status_code == 404


def test_performance(s):
    r = s.get(f"{API}/students/stu_001/performance", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert "timeline" in data and isinstance(data["timeline"], list)
    assert "attempts" in data and isinstance(data["attempts"], list)
    assert len(data["attempts"]) > 0


def test_weak_topics(s):
    r = s.get(f"{API}/students/stu_001/weak-topics", timeout=15)
    assert r.status_code == 200
    data = r.json()
    assert "weak_topics" in data
    assert "subject_scores" in data
    assert isinstance(data["subject_scores"], dict)


def test_predict(s):
    r = s.post(f"{API}/students/stu_001/predict", timeout=15)
    assert r.status_code == 200
    data = r.json()
    for k in ("risk", "fail_probability_pct", "pass_probability_pct", "trend", "reasoning"):
        assert k in data
    assert 0 <= data["fail_probability_pct"] <= 100
    assert 0 <= data["pass_probability_pct"] <= 100


def test_recommendations(s):
    r = s.post(f"{API}/students/stu_001/recommendations", json={"refresh": True}, timeout=45)
    assert r.status_code == 200
    data = r.json()
    assert "recommendations" in data
    recs = data["recommendations"]
    assert isinstance(recs, list) and len(recs) >= 1
    first = recs[0]
    for k in ("type", "title", "subject", "reason", "duration_min"):
        assert k in first, f"recommendation missing {k}"


# -------- Quizzes --------
def test_list_quizzes(s):
    r = s.get(f"{API}/quizzes", timeout=15)
    assert r.status_code == 200
    arr = r.json()
    assert len(arr) == 6
    for q in arr:
        assert "question_count" in q
        # answers must be stripped
        for qq in q["questions"]:
            assert "answer" not in qq


def test_get_quiz(s):
    r = s.get(f"{API}/quizzes/qz_001", timeout=15)
    assert r.status_code == 200
    qz = r.json()
    assert qz["id"] == "qz_001"
    for qq in qz["questions"]:
        assert "answer" not in qq


def test_get_quiz_404(s):
    r = s.get(f"{API}/quizzes/invalid", timeout=15)
    assert r.status_code == 404


def test_quiz_attempt_and_persistence(s):
    # Submit attempt - all option index 0 to be deterministic
    payload = {"student_id": "stu_001", "answers": [0, 0, 0, 0, 0], "time_spent_min": 7}
    r = s.post(f"{API}/quizzes/qz_001/attempt", json=payload, timeout=15)
    assert r.status_code == 200
    data = r.json()
    for k in ("attempt", "correct", "total", "score"):
        assert k in data
    assert data["total"] == 5
    attempt_id = data["attempt"]["id"]

    # Verify persisted via performance endpoint
    r2 = s.get(f"{API}/students/stu_001/performance", timeout=15)
    assert r2.status_code == 200
    ids = [a["id"] for a in r2.json()["attempts"]]
    assert attempt_id in ids


def test_quiz_attempt_invalid(s):
    r = s.post(f"{API}/quizzes/invalid/attempt",
               json={"student_id": "stu_001", "answers": [0]}, timeout=15)
    assert r.status_code == 404


# -------- Teacher --------
def test_class_overview(s):
    r = s.get(f"{API}/teacher/class-overview", timeout=20)
    assert r.status_code == 200
    data = r.json()
    for k in ("total_students", "class_avg", "at_risk_count",
              "total_engagement_min", "topics_covered", "subject_avg"):
        assert k in data
    assert data["total_students"] == 10


def test_heatmap(s):
    r = s.get(f"{API}/teacher/heatmap", timeout=20)
    assert r.status_code == 200
    data = r.json()
    assert "subjects" in data and len(data["subjects"]) == 6
    assert "rows" in data and len(data["rows"]) == 10
    row = data["rows"][0]
    assert "student_id" in row and "name" in row and "scores" in row


def test_at_risk(s):
    r = s.get(f"{API}/teacher/at-risk", timeout=20)
    assert r.status_code == 200
    arr = r.json()
    assert isinstance(arr, list)
    # all returned students must be HIGH or MEDIUM risk
    for st in arr:
        assert st["risk"] in ("HIGH", "MEDIUM")
    # sorted ascending by avg_score
    if len(arr) > 1:
        scores = [st["avg_score"] for st in arr]
        assert scores == sorted(scores)


# -------- AI Tutor --------
def test_ai_tutor_chat_and_history(s):
    payload = {"student_id": "stu_001", "session_id": "test_session_001",
               "message": "Help me understand fractions briefly."}
    r = s.post(f"{API}/ai-tutor/chat", json=payload, timeout=45)
    assert r.status_code == 200
    data = r.json()
    assert "reply" in data and "session_id" in data
    assert isinstance(data["reply"], str) and len(data["reply"]) > 0
    time.sleep(1)
    r2 = s.get(f"{API}/ai-tutor/history/stu_001", timeout=15)
    assert r2.status_code == 200
    arr = r2.json()
    assert isinstance(arr, list) and len(arr) >= 1
    # latest must have user_message we sent (or contain it among history)
    msgs = [m["user_message"] for m in arr]
    assert any("fractions" in m for m in msgs)


def test_ai_tutor_invalid_student(s):
    r = s.post(f"{API}/ai-tutor/chat",
               json={"student_id": "nonexistent", "message": "hi"}, timeout=15)
    assert r.status_code == 404
