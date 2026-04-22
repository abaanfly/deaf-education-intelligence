"""Open-education dataset registry.

Each dataset has a bundled JSON file with `{meta, records}` shape plus a pure
Python transformer that maps one record to `(student_dict, attempts_list)`.
The admin router exposes info / import / reset operations over any registered
dataset, all sharing a `source=<key>` tag so resets are non-destructive for the
curated seed data and for other datasets.
"""
from __future__ import annotations
import hashlib
import json
import random
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple
from fastapi import HTTPException

from core.db import db, SUBJECTS, ROOT_DIR

DATASETS_DIR = ROOT_DIR / "datasets"

# Transformer returns (student_doc, list_of_attempt_docs) WITHOUT the `source`
# or `student_id` fields — the registry fills those in consistently.
Transformer = Callable[[Dict[str, Any], datetime], Tuple[Dict[str, Any], List[Dict[str, Any]]]]


@dataclass
class DatasetSpec:
    key: str
    file_name: str
    ext_id_field: str  # which record field is the stable external id
    transform: Transformer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _stable_int(ext_id: str, mod: int) -> int:
    digest = hashlib.md5(str(ext_id).encode("utf-8")).hexdigest()
    return int(digest, 16) % mod


def _avatar(ext_id: str) -> str:
    return f"https://i.pravatar.cc/200?img={_stable_int(ext_id, 70) + 1}"


def _mk_attempt(student_id: str, subject: str, score: int, minutes: int, days_ago: int) -> Dict[str, Any]:
    return {
        "id": f"att_{uuid.uuid4().hex[:10]}",
        "student_id": student_id,
        "quiz_id": "qz_imported",
        "subject": subject,
        "score": max(0, min(100, int(score))),
        "time_spent_min": max(1, int(minutes)),
        "completed_at": (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat(),
    }


# ---------------------------------------------------------------------------
# UCI Student Performance
# ---------------------------------------------------------------------------
def _transform_uci(row: Dict[str, Any], now: datetime) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    student_id = f"uci_{row['ext_id'].lower()}"
    student = {
        "id": student_id,
        "ext_id": row["ext_id"],
        "name": row["name"],
        "grade": f"Age {row['age']}",
        "avatar": _avatar(row["ext_id"]),
        "joined_at": (now - timedelta(days=60 + _stable_int(row["ext_id"], 120))).isoformat(),
        "meta": {
            "sex": row["sex"], "age": row["age"],
            "studytime": row["studytime"],
            "failures": row["failures"], "absences": row["absences"],
        },
    }
    rng = random.Random(row["ext_id"])
    time_min = 5 + row["studytime"] * 5
    attempts = []
    for subject in SUBJECTS:
        for grade_val, days_ago in ((row["G1"], 42), (row["G2"], 21), (row["G3"], 7)):
            score = int(round((grade_val / 20.0) * 100)) + rng.randint(-8, 8)
            attempts.append(
                _mk_attempt(
                    student_id, subject, score,
                    time_min + rng.randint(-3, 3),
                    days_ago + rng.randint(0, 5),
                )
            )
    return student, attempts


# ---------------------------------------------------------------------------
# OULAD
# ---------------------------------------------------------------------------
_OULAD_MODULE_TO_SUBJECT = {
    "AAA": "Algebra", "BBB": "Geometry", "CCC": "Biology",
    "DDD": "Physics", "EEE": "English Grammar", "FFF": "World History",
    "GGG": "Algebra",  # spillover module
}
_OULAD_RESULT_TO_BASE = {
    "Distinction": 88, "Pass": 72, "Fail": 42, "Withdrawn": 35,
}


def _transform_oulad(row: Dict[str, Any], now: datetime) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    sid = str(row["id_student"])
    student_id = f"oulad_{sid}"
    student = {
        "id": student_id,
        "ext_id": sid,
        "name": f"OU Learner #{sid}",
        "grade": row["age_band"],
        "avatar": _avatar(sid),
        "joined_at": (now - timedelta(days=120 + _stable_int(sid, 90))).isoformat(),
        "meta": {
            "gender": row["gender"],
            "code_module": row["code_module"],
            "studied_credits": row["studied_credits"],
            "num_of_prev_attempts": row["num_of_prev_attempts"],
            "final_result": row["final_result"],
            "sum_click": row["sum_click"],
        },
    }
    rng = random.Random(sid)
    primary_subject = _OULAD_MODULE_TO_SUBJECT.get(row["code_module"], SUBJECTS[0])
    base = _OULAD_RESULT_TO_BASE.get(row["final_result"], 55)
    # Prior failures drag down; click engagement lifts up
    base -= int(row["num_of_prev_attempts"]) * 4
    base += min(12, row["sum_click"] // 200)
    # Minutes from clicks: ~1 click = 0.25 min, capped
    minutes = max(5, min(40, row["sum_click"] // 60))

    attempts = []
    # 4 attempts on primary module, 2 attempts on each other subject (varied)
    for days_ago in (56, 35, 21, 7):
        score = base + rng.randint(-6, 6)
        attempts.append(_mk_attempt(student_id, primary_subject, score, minutes, days_ago))

    for subject in SUBJECTS:
        if subject == primary_subject:
            continue
        for days_ago in (42, 14):
            score = base + rng.randint(-14, 10) - 4
            attempts.append(_mk_attempt(student_id, subject, score, minutes - 2, days_ago))
    return student, attempts


# ---------------------------------------------------------------------------
# Kaggle xAPI-Edu
# ---------------------------------------------------------------------------
_XAPI_TOPIC_TO_SUBJECT = {
    "Math": "Algebra",
    "Science": "Biology",
    "English": "English Grammar",
    "History": "World History",
    "IT": "Physics",
}
_XAPI_CLASS_TO_BASE = {"L": 42, "M": 65, "H": 85}


def _transform_xapi(row: Dict[str, Any], now: datetime) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    sid = row["ext_id"]
    student_id = f"xapi_{sid.lower()}"
    engagement = (
        row["raisedhands"] + row["VisITedResources"]
        + row["AnnouncementsView"] + row["Discussion"]
    )
    student = {
        "id": student_id,
        "ext_id": sid,
        "name": row["name"],
        "grade": f"Section {row['SectionID']}",
        "avatar": _avatar(sid),
        "joined_at": (now - timedelta(days=50 + _stable_int(sid, 90))).isoformat(),
        "meta": {
            "gender": row["gender"],
            "Topic": row["Topic"],
            "raisedhands": row["raisedhands"],
            "VisITedResources": row["VisITedResources"],
            "AnnouncementsView": row["AnnouncementsView"],
            "Discussion": row["Discussion"],
            "StudentAbsenceDays": row["StudentAbsenceDays"],
            "Class": row["Class"],
            "engagement_index": engagement,
        },
    }
    rng = random.Random(sid)
    primary_subject = _XAPI_TOPIC_TO_SUBJECT.get(row["Topic"], SUBJECTS[0])
    base = _XAPI_CLASS_TO_BASE.get(row["Class"], 60)
    # Engagement nudge
    base += min(10, engagement // 40)
    if row["StudentAbsenceDays"] == "Above-7":
        base -= 8
    minutes = max(6, min(30, engagement // 12))

    attempts = []
    for days_ago in (49, 28, 14, 5):
        score = base + rng.randint(-7, 7)
        attempts.append(_mk_attempt(student_id, primary_subject, score, minutes, days_ago))

    for subject in SUBJECTS:
        if subject == primary_subject:
            continue
        for days_ago in (42, 10):
            score = base + rng.randint(-12, 8) - 5
            attempts.append(_mk_attempt(student_id, subject, score, minutes - 2, days_ago))
    return student, attempts


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
DATASETS: Dict[str, DatasetSpec] = {
    "uci": DatasetSpec("uci", "uci_students.json", "ext_id", _transform_uci),
    "oulad": DatasetSpec("oulad", "oulad_sample.json", "id_student", _transform_oulad),
    "kaggle_xapi": DatasetSpec("kaggle_xapi", "kaggle_xapi.json", "ext_id", _transform_xapi),
}


def _load_bundle(spec: DatasetSpec) -> Dict[str, Any]:
    path = DATASETS_DIR / spec.file_name
    if not path.exists():
        raise HTTPException(500, f"Dataset file missing: {spec.file_name}")
    with open(path) as fh:
        return json.load(fh)


def _require(key: str) -> DatasetSpec:
    if key not in DATASETS:
        raise HTTPException(404, f"Unknown dataset '{key}'")
    return DATASETS[key]


# ---------------------------------------------------------------------------
# Public API (called by routers/admin.py)
# ---------------------------------------------------------------------------
async def list_datasets() -> List[Dict[str, Any]]:
    out = []
    for spec in DATASETS.values():
        bundle = _load_bundle(spec)
        meta = bundle.get("meta", {})
        records = bundle.get("records", [])
        imported = await db.students.count_documents({"source": f"dataset:{spec.key}"})
        out.append(
            {
                "key": spec.key,
                "name": meta.get("name", spec.key),
                "source": meta.get("source", ""),
                "available_records": len(records),
                "already_imported": imported,
            }
        )
    return out


async def dataset_info(key: str) -> Dict[str, Any]:
    spec = _require(key)
    bundle = _load_bundle(spec)
    meta = bundle.get("meta", {})
    records = bundle.get("records", [])
    imported = await db.students.count_documents({"source": f"dataset:{spec.key}"})
    return {
        "key": spec.key,
        "name": meta.get("name", spec.key),
        "source": meta.get("source", ""),
        "available_records": len(records),
        "already_imported": imported,
    }


async def import_dataset(key: str) -> Dict[str, Any]:
    spec = _require(key)
    bundle = _load_bundle(spec)
    records = bundle.get("records", [])
    tag = f"dataset:{spec.key}"

    existing = {
        str(s["ext_id"])
        async for s in db.students.find({"source": tag}, {"ext_id": 1, "_id": 0})
    }
    now = datetime.now(timezone.utc)
    new_students: List[Dict[str, Any]] = []
    new_attempts: List[Dict[str, Any]] = []

    for row in records:
        ext_id = str(row[spec.ext_id_field])
        if ext_id in existing:
            continue
        # Normalize ext_id onto the record so the transformer sees it.
        row = {**row, "ext_id": ext_id}
        student, attempts = spec.transform(row, now)
        student["source"] = tag
        new_students.append(student)
        for a in attempts:
            a["source"] = tag
            new_attempts.append(a)

    if new_students:
        await db.students.insert_many(new_students)
    if new_attempts:
        await db.quiz_attempts.insert_many(new_attempts)

    return {
        "key": spec.key,
        "imported_students": len(new_students),
        "imported_attempts": len(new_attempts),
        "already_existed": len(existing),
        "dataset": bundle.get("meta", {}).get("name", spec.key),
    }


async def reset_dataset(key: str) -> Dict[str, Any]:
    spec = _require(key)
    tag = f"dataset:{spec.key}"
    dels = await db.students.delete_many({"source": tag})
    dela = await db.quiz_attempts.delete_many({"source": tag})
    return {
        "key": spec.key,
        "deleted_students": dels.deleted_count,
        "deleted_attempts": dela.deleted_count,
    }


async def reset_all_datasets() -> Dict[str, Any]:
    deleted = {}
    total_students = 0
    total_attempts = 0
    for key in DATASETS:
        res = await reset_dataset(key)
        deleted[key] = res
        total_students += res["deleted_students"]
        total_attempts += res["deleted_attempts"]
    # Legacy cleanup: earlier versions tagged UCI imports as 'uci_open_dataset'
    legacy_s = await db.students.delete_many({"source": "uci_open_dataset"})
    legacy_a = await db.quiz_attempts.delete_many({"source": "uci_open_dataset"})
    if legacy_s.deleted_count or legacy_a.deleted_count:
        deleted["_legacy"] = {
            "deleted_students": legacy_s.deleted_count,
            "deleted_attempts": legacy_a.deleted_count,
        }
        total_students += legacy_s.deleted_count
        total_attempts += legacy_a.deleted_count
    return {
        "deleted_students": total_students,
        "deleted_attempts": total_attempts,
        "per_dataset": deleted,
    }
