# DEIS — Deaf Education Intelligence System (PRD)

## Original Problem Statement
AI-powered learning intelligence platform designed to personalize education for Deaf & Hard-of-Hearing students. Tracks learning behavior, predicts performance, detects weak concepts, and recommends personalized learning paths — turning accessibility into actionable intelligence.

## User Choices (2026-04-20)
- Scope: Full app (Student + Teacher dashboards)
- AI approach: Rule-based scoring + LLM-powered recommendations & AI tutor (Claude Sonnet 4.5 via Emergent Universal Key)
- Authentication: No auth — role switcher for demo
- Data: Rich seeded demo data
- Design: Dark mode, modern startup-level UI (Outfit + Manrope fonts, #FF7A59 / #38BDF8 accents)

## User Personas
- **Student** (Deaf / HoH): tracks own progress, takes quizzes, chats with AI tutor, gets visual-first recommendations.
- **Teacher**: monitors whole class, identifies at-risk students, reviews topic heatmap, drills into individuals.

## Architecture
- **Backend** (FastAPI, modular as of iter 4):
  - `server.py` — slim (~55 LOC): FastAPI app + router wiring + lifecycle
  - `core/` — shared infrastructure (`db`, `llm`, `analytics`, `seed`, `security`, `models`)
  - `routers/` — domain modules (`students`, `quizzes`, `teacher`, `tutor`, `admin`)
  - `datasets/uci_students.json` — bundled open-education sample (30 records)
- **Frontend** (React + Tailwind + Recharts + sonner): pages `LandingPage`, `StudentDashboard`, `TeacherDashboard`, `QuizPage`. Shared `AppShell` and components `StatCard`, `PerformanceChart`, `WeakTopicsPanel`, `AIRecommendations`, `AITutorChat`, `RiskAlerts`, `TopicHeatmap`, `StudentTable`, `TeacherActions`, `EncouragementDialog`.
- **Admin guard** — `/api/admin/*` endpoints require `X-Admin-Token` header matching backend `ADMIN_TOKEN` env (and frontend `REACT_APP_ADMIN_TOKEN`).

## What's Been Implemented (2026-04-20)
### Backend endpoints
- `GET /api/` health
- `GET /api/students` (list w/ stats) · `GET /api/students/{id}` · `/performance` · `/weak-topics`
- `POST /api/students/{id}/recommendations` — LLM-powered 4-item personalized list (Claude 4.5)
- `POST /api/students/{id}/predict` — rule-based risk & pass-probability
- `GET /api/quizzes` · `GET /api/quizzes/{id}` · `POST /api/quizzes/{id}/attempt`
- `GET /api/teacher/class-overview` · `/heatmap` · `/at-risk`
- `POST /api/ai-tutor/chat` · `GET /api/ai-tutor/history/{student_id}`
- **Iter 3 new**: `POST /api/students/{id}/encouragement` + `GET /encouragements` (LLM-drafted messages, persisted)
- **Iter 3 new**: `GET /api/teacher/export/csv` · `GET /api/teacher/export/pdf` (reportlab branded report)
- **Iter 3 new**: `GET /api/admin/open-dataset/info` · `POST /import` · `POST /reset` (bundled UCI Student Performance sample, 30 records)
- Idempotent seed: 10 students, 6 quizzes, ~123 synthetic attempts spread over 8 weeks
- **Test coverage**: 25/25 backend tests passed (iteration 3)

### Frontend
- Landing page with role switcher, gradient hero, feature pills
- Student dashboard: 4 KPI cards, performance area chart, AI recommendations (LLM), weak topics panel, AI tutor chat with **persistent history across visits**, practice quizzes grid
- Teacher dashboard: 4 KPI cards, subject performance bar chart, at-risk alerts (with **per-row Send Encouragement heart button**), topic heatmap, class roster table (click → drill down), toolbar with **Export CSV / Export PDF / Open dataset** actions
- Quiz page: take 5-Q quiz, auto-scored, attempts flow back into analytics
- All 100% frontend flows verified (iterations 1–3)

## Prioritized Backlog
### P1 (nice-to-have next)
- Multi-language sign-language interpreter overlays
- Caption usage tracking as an engagement signal
- Export class report CSV/PDF for teachers
- Real auth (JWT or Emergent Google) so teachers see only their classes

### P2
- Mobile responsive polish for heatmap table
- Notification center for at-risk alerts
- Assignment module (longer-form than quizzes)
- AI Tutor persistence across sessions

## Next Tasks
- Hook in additional open-education datasets (Kaggle, OULAD)
- Replace deprecated `@app.on_event` with FastAPI lifespan context manager
- Add teacher "Send encouragement" action on at-risk row
- Consider Bearer-style auth for a real production rollout (admin token is demo-grade only)
