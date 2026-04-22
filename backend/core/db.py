"""Database client, env constants, and shared immutables."""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

MONGO_URL = os.environ["MONGO_URL"]
DB_NAME = os.environ["DB_NAME"]
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

_client = AsyncIOMotorClient(MONGO_URL)
db = _client[DB_NAME]


def close_client() -> None:
    _client.close()


SUBJECTS = [
    "Algebra",
    "Geometry",
    "Biology",
    "Physics",
    "English Grammar",
    "World History",
]

DATASET_PATH = ROOT_DIR / "datasets" / "uci_students.json"
