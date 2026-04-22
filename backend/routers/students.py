"""Student-facing endpoints: list, detail, performance, weak topics, AI recs, predict."""
from __future__ import annotations
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException
from core.db import db
from core.analytics import student_attempts, student_stats
from core.llm import llm_chat
from core.models import RecommendationRequest

router = APIRouter(prefix="/students", tags=["students"])


@router.get("")
async def list_students():
    students = await db.students.find({}, {"_id": 0}).to_list(1000)
    enriched = []
    for s in students:
        stats = await student_stats(s["id"])
        enriched.append({**s, **stats})
    return enriched


@router.get("/{student_id}")
async def get_student(student_id: str):
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(404, "Student not found")
    stats = await student_stats(student_id)
    return {**student, **stats}


@router.get("/{student_id}/performance")
async def performance_timeline(student_id: str):
    attempts = await student_attempts(student_id)
    buckets: Dict[str, List[int]] = {}
    for a in attempts:
        dt = datetime.fromisoformat(a["completed_at"])
        week_key = dt.strftime("Week %V")
        buckets.setdefault(week_key, []).append(a["score"])
    timeline = [
        {"week": k, "score": round(sum(v) / len(v), 1), "attempts": len(v)}
        for k, v in buckets.items()
    ]
    return {"timeline": timeline, "attempts": attempts}


@router.get("/{student_id}/weak-topics")
async def weak_topics(student_id: str):
    stats = await student_stats(student_id)
    return {
        "weak_topics": stats["weak_topics"],
        "subject_scores": stats["subject_scores"],
    }


@router.post("/{student_id}/recommendations")
async def recommendations(student_id: str, body: RecommendationRequest):  # noqa: ARG001
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(404, "Student not found")
    stats = await student_stats(student_id)

    if not stats["weak_topics"]:
        weak_list = "No significant weak topics — student is performing well across subjects."
    else:
        weak_list = ", ".join(f"{w['subject']} ({w['score']}%)" for w in stats["weak_topics"])

    system = (
        "You are an AI learning coach for Deaf and Hard-of-Hearing students. "
        "Your recommendations must favor visual-first content, short sentences, and concrete practice steps. "
        "Always format output as a JSON array of 4 objects with keys: "
        "{type: 'video'|'practice'|'reading'|'visual', title, subject, reason, duration_min}. "
        "Return ONLY the JSON array, no extra prose."
    )
    prompt = (
        f"Student: {student['name']} ({student['grade']}). "
        f"Overall avg: {stats['avg_score']}%. Risk: {stats['risk']}. "
        f"Weak topics: {weak_list}. "
        f"Subject scores: {stats['subject_scores']}. "
        "Produce 4 personalized recommendations."
    )
    text = await llm_chat(f"rec_{student_id}", system, prompt)

    recs: List[Dict[str, Any]] = []
    try:
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            recs = json.loads(match.group(0))
    except Exception:
        recs = []

    if not recs:
        fallback = []
        for w in stats["weak_topics"][:3]:
            fallback.append(
                {
                    "type": "visual",
                    "title": f"Visual walkthrough: {w['subject']}",
                    "subject": w["subject"],
                    "reason": (
                        f"Your {w['subject']} average is {w['score']}% — a visual "
                        "lesson helps anchor concepts."
                    ),
                    "duration_min": 12,
                }
            )
        fallback.append(
            {
                "type": "practice",
                "title": "5-question focus drill",
                "subject": stats["weak_topics"][0]["subject"]
                if stats["weak_topics"]
                else "Mixed",
                "reason": "Short practice sets build confidence without fatigue.",
                "duration_min": 10,
            }
        )
        recs = fallback

    return {
        "recommendations": recs,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/{student_id}/predict")
async def predict_risk(student_id: str):
    stats = await student_stats(student_id)
    avg = stats["avg_score"]
    trend = stats["weekly_progress"]
    fail = max(0, min(100, int((70 - avg) * 1.8 - trend * 1.2)))
    return {
        "risk": stats["risk"],
        "fail_probability_pct": max(0, fail),
        "pass_probability_pct": 100 - max(0, fail),
        "trend": trend,
        "reasoning": (
            f"Based on {stats['total_attempts']} attempts with avg {avg}% and "
            f"{'improving' if trend > 0 else 'declining'} trend of {trend} pts."
        ),
    }
