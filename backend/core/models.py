"""Pydantic request/response models shared across routers."""
from typing import List, Optional
from pydantic import BaseModel


class AttemptSubmit(BaseModel):
    student_id: str
    answers: List[int]
    time_spent_min: int = 10


class TutorChatRequest(BaseModel):
    student_id: str
    session_id: Optional[str] = None
    message: str


class RecommendationRequest(BaseModel):
    refresh: bool = False


class EncouragementRequest(BaseModel):
    note: Optional[str] = None
