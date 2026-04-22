"""Quiz listing, detail, and attempt submission."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from core.db import db
from core.models import AttemptSubmit

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("")
async def list_quizzes():
    quizzes = await db.quizzes.find({}, {"_id": 0}).to_list(100)
    for q in quizzes:
        q["question_count"] = len(q.get("questions", []))
        q["questions"] = [
            {"q": qq["q"], "options": qq["options"]} for qq in q.get("questions", [])
        ]
    return quizzes


@router.get("/{quiz_id}")
async def get_quiz(quiz_id: str):
    qz = await db.quizzes.find_one({"id": quiz_id}, {"_id": 0})
    if not qz:
        raise HTTPException(404, "Quiz not found")
    qz["questions"] = [
        {"q": qq["q"], "options": qq["options"]} for qq in qz.get("questions", [])
    ]
    return qz


@router.post("/{quiz_id}/attempt")
async def submit_attempt(quiz_id: str, body: AttemptSubmit):
    qz = await db.quizzes.find_one({"id": quiz_id}, {"_id": 0})
    if not qz:
        raise HTTPException(404, "Quiz not found")

    correct = sum(
        1
        for i, ans in enumerate(body.answers)
        if i < len(qz["questions"]) and qz["questions"][i]["answer"] == ans
    )
    total = len(qz["questions"])
    score = int(round(correct / total * 100)) if total else 0

    attempt = {
        "id": f"att_{uuid.uuid4().hex[:10]}",
        "student_id": body.student_id,
        "quiz_id": quiz_id,
        "subject": qz["subject"],
        "score": score,
        "time_spent_min": body.time_spent_min,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.quiz_attempts.insert_one(attempt.copy())
    return {"attempt": attempt, "correct": correct, "total": total, "score": score}
