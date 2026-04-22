"""DEIS — Deaf Education Intelligence System.

Slim FastAPI entrypoint. Wires routers and lifecycle. Domain logic lives in
`core/` and `routers/`.
"""
from __future__ import annotations
import logging
import os
from fastapi import APIRouter, FastAPI
from starlette.middleware.cors import CORSMiddleware

from core.db import close_client
from core.seed import seed_database
from routers import students, quizzes, teacher, tutor, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="DEIS API")
api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"service": "DEIS", "status": "ok"}


# Feature routers
api_router.include_router(students.router)
api_router.include_router(quizzes.router)
api_router.include_router(teacher.router)
api_router.include_router(tutor.router)
api_router.include_router(admin.router)

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    await seed_database()


@app.on_event("shutdown")
async def on_shutdown():
    close_client()
