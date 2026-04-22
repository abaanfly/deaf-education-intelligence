"""Idempotent MongoDB seeding — runs once on startup."""
from __future__ import annotations
import logging
import random
import uuid
from datetime import datetime, timezone, timedelta
from core.db import db, SUBJECTS

logger = logging.getLogger(__name__)

STUDENT_NAMES = [
    ("Ayesha Patel", "Grade 10", "https://images.unsplash.com/photo-1721468184185-214871ec4411?crop=entropy&cs=srgb&fm=jpg&w=200&q=85"),
    ("Marcus Johnson", "Grade 10", "https://images.pexels.com/photos/6684506/pexels-photo-6684506.jpeg?auto=compress&cs=tinysrgb&w=200"),
    ("Lin Chen", "Grade 10", "https://i.pravatar.cc/200?img=47"),
    ("Sofia Rodriguez", "Grade 10", "https://i.pravatar.cc/200?img=45"),
    ("Jamal Carter", "Grade 10", "https://i.pravatar.cc/200?img=12"),
    ("Priya Sharma", "Grade 10", "https://i.pravatar.cc/200?img=16"),
    ("Noah Williams", "Grade 10", "https://i.pravatar.cc/200?img=33"),
    ("Emma Kowalski", "Grade 10", "https://i.pravatar.cc/200?img=20"),
    ("Daniel Park", "Grade 10", "https://i.pravatar.cc/200?img=15"),
    ("Zainab Hassan", "Grade 10", "https://i.pravatar.cc/200?img=23"),
]

SAMPLE_QUIZZES = [
    {
        "title": "Algebra Foundations",
        "subject": "Algebra",
        "difficulty": "Easy",
        "questions": [
            {"q": "Solve for x: 2x + 6 = 14", "options": ["2", "4", "6", "8"], "answer": 1},
            {"q": "Simplify: 3(x + 2) - x", "options": ["2x + 6", "3x + 6", "4x + 6", "2x + 2"], "answer": 0},
            {"q": "If y = 2x + 3 and x = 4, find y", "options": ["8", "10", "11", "14"], "answer": 2},
            {"q": "Factor: x² - 9", "options": ["(x-3)²", "(x+3)²", "(x-3)(x+3)", "x(x-9)"], "answer": 2},
            {"q": "Solve: x/3 = 7", "options": ["21", "10", "4", "3"], "answer": 0},
        ],
    },
    {
        "title": "Grammar Essentials",
        "subject": "English Grammar",
        "difficulty": "Easy",
        "questions": [
            {"q": "Choose the correct verb: She ___ to school every day.", "options": ["go", "goes", "gone", "going"], "answer": 1},
            {"q": "Identify the noun: The cat sleeps on the mat.", "options": ["sleeps", "on", "cat", "the"], "answer": 2},
            {"q": "Past tense of 'run' is:", "options": ["runs", "runned", "ran", "running"], "answer": 2},
            {"q": "Which is a pronoun?", "options": ["Quickly", "She", "Apple", "Blue"], "answer": 1},
            {"q": "Select the correct article: ___ hour ago.", "options": ["A", "An", "The", "No article"], "answer": 1},
        ],
    },
    {
        "title": "Physics: Motion Basics",
        "subject": "Physics",
        "difficulty": "Medium",
        "questions": [
            {"q": "Unit of acceleration is:", "options": ["m/s", "m/s²", "N", "J"], "answer": 1},
            {"q": "Speed = distance / ___", "options": ["mass", "force", "time", "energy"], "answer": 2},
            {"q": "Newton's 1st Law is about:", "options": ["F=ma", "Inertia", "Gravity", "Friction"], "answer": 1},
            {"q": "Gravitational acceleration on Earth ≈", "options": ["5 m/s²", "9.8 m/s²", "15 m/s²", "1 m/s²"], "answer": 1},
            {"q": "A body at rest stays at rest unless…", "options": ["it rains", "a force acts", "it moves", "time passes"], "answer": 1},
        ],
    },
    {
        "title": "Biology: Cells 101",
        "subject": "Biology",
        "difficulty": "Easy",
        "questions": [
            {"q": "Powerhouse of the cell:", "options": ["Nucleus", "Mitochondria", "Ribosome", "Lysosome"], "answer": 1},
            {"q": "Cell wall is found in:", "options": ["Animal cells", "Plant cells", "Both", "Neither"], "answer": 1},
            {"q": "DNA is located in the:", "options": ["Cytoplasm", "Nucleus", "Membrane", "Wall"], "answer": 1},
            {"q": "Photosynthesis happens in:", "options": ["Mitochondria", "Chloroplast", "Nucleus", "Golgi"], "answer": 1},
            {"q": "Basic unit of life:", "options": ["Atom", "Molecule", "Cell", "Organ"], "answer": 2},
        ],
    },
    {
        "title": "Geometry Basics",
        "subject": "Geometry",
        "difficulty": "Medium",
        "questions": [
            {"q": "Sum of interior angles of a triangle:", "options": ["90°", "180°", "270°", "360°"], "answer": 1},
            {"q": "Area of rectangle = length × ___", "options": ["width", "height", "angle", "radius"], "answer": 0},
            {"q": "π ≈", "options": ["2.14", "3.14", "4.14", "1.14"], "answer": 1},
            {"q": "A right angle is:", "options": ["45°", "60°", "90°", "180°"], "answer": 2},
            {"q": "Shape with 4 equal sides + right angles:", "options": ["Rectangle", "Rhombus", "Square", "Trapezoid"], "answer": 2},
        ],
    },
    {
        "title": "World History Snapshot",
        "subject": "World History",
        "difficulty": "Medium",
        "questions": [
            {"q": "WWII ended in:", "options": ["1939", "1945", "1918", "1950"], "answer": 1},
            {"q": "Who invented the printing press?", "options": ["Edison", "Gutenberg", "Newton", "Ford"], "answer": 1},
            {"q": "Great Wall is in:", "options": ["India", "China", "Japan", "Korea"], "answer": 1},
            {"q": "Renaissance began in:", "options": ["France", "Italy", "Spain", "Germany"], "answer": 1},
            {"q": "Industrial Revolution started in:", "options": ["USA", "Germany", "England", "France"], "answer": 2},
        ],
    },
]


async def seed_database() -> None:
    """Seed students, quizzes, and synthetic attempts. Idempotent."""
    n_students = await db.students.count_documents({})
    if n_students > 0:
        return

    now = datetime.now(timezone.utc)
    students = [
        {
            "id": f"stu_{idx+1:03d}",
            "name": name,
            "grade": grade,
            "avatar": avatar,
            "joined_at": (now - timedelta(days=random.randint(30, 200))).isoformat(),
        }
        for idx, (name, grade, avatar) in enumerate(STUDENT_NAMES)
    ]
    await db.students.insert_many(students)

    quizzes = [
        {
            "id": f"qz_{idx+1:03d}",
            "title": q["title"],
            "subject": q["subject"],
            "difficulty": q["difficulty"],
            "questions": q["questions"],
        }
        for idx, q in enumerate(SAMPLE_QUIZZES)
    ]
    await db.quizzes.insert_many(quizzes)

    attempts = []
    for s in students:
        ability = {subj: random.randint(40, 92) for subj in SUBJECTS}
        weak = random.choice(SUBJECTS)
        ability[weak] = random.randint(30, 55)

        for week in range(8):
            for _ in range(random.randint(1, 2)):
                qz = random.choice(quizzes)
                base = ability[qz["subject"]]
                noise = random.randint(-10, 10)
                trend = week * 1.5
                score = max(0, min(100, int(base + noise + trend)))
                attempts.append(
                    {
                        "id": f"att_{uuid.uuid4().hex[:10]}",
                        "student_id": s["id"],
                        "quiz_id": qz["id"],
                        "subject": qz["subject"],
                        "score": score,
                        "time_spent_min": random.randint(6, 25),
                        "completed_at": (
                            now - timedelta(days=(7 - week) * 7 + random.randint(0, 6))
                        ).isoformat(),
                    }
                )
    await db.quiz_attempts.insert_many(attempts)
    logger.info(
        "Seeded %d students, %d quizzes, %d attempts",
        len(students), len(quizzes), len(attempts),
    )
