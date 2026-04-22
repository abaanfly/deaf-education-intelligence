"""AI Tutor chat + history, and teacher-sent encouragement messages."""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from core.db import db
from core.analytics import student_stats
from core.llm import llm_chat
from core.models import TutorChatRequest, EncouragementRequest

router = APIRouter(tags=["tutor"])


@router.post("/ai-tutor/chat")
async def ai_tutor_chat(body: TutorChatRequest):
    student = await db.students.find_one({"id": body.student_id}, {"_id": 0})
    if not student:
        raise HTTPException(404, "Student not found")
    stats = await student_stats(body.student_id)

    system = (
        "You are DEIS Tutor, a kind, patient AI learning coach for Deaf and Hard-of-Hearing students. "
        "Rules: (1) Use short, simple sentences. (2) Prefer visual metaphors and step-by-step explanations. "
        "(3) Never assume audio context. (4) Encourage and celebrate progress. "
        "(5) Keep replies under 120 words unless the student asks for depth."
    )
    session_id = body.session_id or f"tutor_{body.student_id}"
    context = (
        f"Student profile — name: {student['name']}, avg: {stats['avg_score']}%, risk: {stats['risk']}, "
        f"weak topics: {[w['subject'] for w in stats['weak_topics']]}. "
        f"Student message: {body.message}"
    )
    reply = await llm_chat(session_id, system, context)

    msg = {
        "id": f"msg_{uuid.uuid4().hex[:10]}",
        "student_id": body.student_id,
        "session_id": session_id,
        "user_message": body.message,
        "assistant_message": reply,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.ai_chats.insert_one(msg.copy())
    return {"session_id": session_id, "reply": reply}


@router.get("/ai-tutor/history/{student_id}")
async def ai_tutor_history(student_id: str):
    msgs = (
        await db.ai_chats.find({"student_id": student_id}, {"_id": 0})
        .sort("created_at", 1)
        .to_list(200)
    )
    return msgs


@router.post("/students/{student_id}/encouragement")
async def send_encouragement(student_id: str, body: EncouragementRequest):
    student = await db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(404, "Student not found")
    stats = await student_stats(student_id)
    weak = ", ".join(w["subject"] for w in stats["weak_topics"]) or "no specific weak area"

    system = (
        "You write short, warm, specific encouragement messages from a teacher to a Deaf/Hard-of-Hearing student. "
        "Tone: caring, never condescending. Keep it under 60 words. "
        "Reference a concrete strength or next step. Avoid audio metaphors. "
        "Return ONLY the message text — no preface, no quotes."
    )
    prompt = (
        f"Student: {student['name']} (avg {stats['avg_score']}%, risk {stats['risk']}, weak: {weak}). "
        f"Teacher note: {body.note or 'no extra note'}. "
        "Write a personalized encouragement message."
    )
    message = await llm_chat(
        f"enc_{student_id}_{uuid.uuid4().hex[:6]}", system, prompt
    )

    record = {
        "id": f"enc_{uuid.uuid4().hex[:10]}",
        "student_id": student_id,
        "student_name": student["name"],
        "message": message.strip(),
        "teacher_note": body.note or "",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.encouragements.insert_one(record.copy())
    return record


@router.get("/students/{student_id}/encouragements")
async def list_encouragements(student_id: str):
    items = (
        await db.encouragements.find({"student_id": student_id}, {"_id": 0})
        .sort("created_at", -1)
        .to_list(100)
    )
    return items
