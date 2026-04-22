"""Derived analytics for a student + helpers used by several routers."""
from __future__ import annotations
from typing import Any, Dict, List
from core.db import db


def risk_level(avg_score: float) -> str:
    if avg_score < 55:
        return "HIGH"
    if avg_score < 70:
        return "MEDIUM"
    return "LOW"


async def student_attempts(student_id: str) -> List[Dict[str, Any]]:
    cursor = (
        db.quiz_attempts.find({"student_id": student_id}, {"_id": 0})
        .sort("completed_at", 1)
    )
    return await cursor.to_list(1000)


async def student_stats(student_id: str) -> Dict[str, Any]:
    attempts = await student_attempts(student_id)
    if not attempts:
        return {
            "avg_score": 0,
            "risk": "LOW",
            "weekly_progress": 0,
            "total_attempts": 0,
            "time_spent_min": 0,
            "weak_topics": [],
            "subject_scores": {},
        }

    scores = [a["score"] for a in attempts]
    avg = sum(scores) / len(scores)

    first_3 = scores[:3]
    last_3 = scores[-3:]
    weekly = round(
        (sum(last_3) / len(last_3)) - (sum(first_3) / len(first_3)), 1
    )

    subj_totals: Dict[str, List[int]] = {}
    for a in attempts:
        subj_totals.setdefault(a["subject"], []).append(a["score"])
    subject_scores = {
        k: round(sum(v) / len(v), 1) for k, v in subj_totals.items()
    }

    weak = [
        {"subject": k, "score": v, "severity": "HIGH" if v < 55 else "MEDIUM"}
        for k, v in sorted(subject_scores.items(), key=lambda x: x[1])
        if v < 70
    ]

    return {
        "avg_score": round(avg, 1),
        "risk": risk_level(avg),
        "weekly_progress": weekly,
        "total_attempts": len(attempts),
        "time_spent_min": sum(a["time_spent_min"] for a in attempts),
        "weak_topics": weak,
        "subject_scores": subject_scores,
    }


async def collect_class_rows() -> List[Dict[str, Any]]:
    students = await db.students.find({}, {"_id": 0}).to_list(1000)
    rows = []
    for s in students:
        rows.append({**s, **(await student_stats(s["id"]))})
    return rows
