"""Teacher-facing endpoints: overview, heatmap, at-risk, CSV + PDF exports."""
from __future__ import annotations
import csv
import io
from datetime import datetime, timezone
from typing import Dict, List
from fastapi import APIRouter
from fastapi.responses import Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from core.db import db, SUBJECTS
from core.analytics import student_stats, collect_class_rows

router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.get("/class-overview")
async def class_overview():
    students = await db.students.find({}, {"_id": 0}).to_list(1000)
    all_stats = [await student_stats(s["id"]) for s in students]
    total = len(all_stats)
    avg_class = (
        round(sum(a["avg_score"] for a in all_stats) / total, 1) if total else 0
    )
    at_risk = sum(1 for a in all_stats if a["risk"] in ("HIGH", "MEDIUM"))
    engagement_min = sum(a["time_spent_min"] for a in all_stats)

    subj_agg: Dict[str, List[float]] = {}
    for a in all_stats:
        for k, v in a["subject_scores"].items():
            subj_agg.setdefault(k, []).append(v)
    subject_avg = {k: round(sum(v) / len(v), 1) for k, v in subj_agg.items()}

    return {
        "total_students": total,
        "class_avg": avg_class,
        "at_risk_count": at_risk,
        "total_engagement_min": engagement_min,
        "topics_covered": len(SUBJECTS),
        "subject_avg": subject_avg,
    }


@router.get("/heatmap")
async def heatmap():
    students = await db.students.find({}, {"_id": 0}).to_list(1000)
    rows = []
    for s in students:
        stats = await student_stats(s["id"])
        rows.append(
            {
                "student_id": s["id"],
                "name": s["name"],
                "scores": {subj: stats["subject_scores"].get(subj) for subj in SUBJECTS},
            }
        )
    return {"subjects": SUBJECTS, "rows": rows}


@router.get("/at-risk")
async def at_risk_students():
    students = await db.students.find({}, {"_id": 0}).to_list(1000)
    alerts = []
    for s in students:
        stats = await student_stats(s["id"])
        if stats["risk"] in ("HIGH", "MEDIUM"):
            alerts.append({**s, **stats})
    alerts.sort(key=lambda x: x["avg_score"])
    return alerts


@router.get("/export/csv")
async def export_class_csv():
    rows = await collect_class_rows()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "Student ID", "Name", "Grade", "Avg Score %", "Risk",
            "Weekly Progress", "Attempts", "Time Spent (min)",
            "Weak Topics", *SUBJECTS,
        ]
    )
    for r in rows:
        weak = "; ".join(f"{w['subject']}({w['score']}%)" for w in r["weak_topics"])
        subj_scores = [r["subject_scores"].get(sub, "") for sub in SUBJECTS]
        writer.writerow(
            [
                r["id"], r["name"], r["grade"], r["avg_score"], r["risk"],
                r["weekly_progress"], r["total_attempts"], r["time_spent_min"],
                weak, *subj_scores,
            ]
        )
    filename = (
        f"deis_class_report_{datetime.now(timezone.utc).strftime('%Y%m%d')}.csv"
    )
    return Response(
        content=buf.getvalue().encode("utf-8"),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/export/pdf")
async def export_class_pdf():
    rows = await collect_class_rows()
    overview = await class_overview()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=letter,
        topMargin=36, bottomMargin=36, leftMargin=36, rightMargin=36,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title", parent=styles["Title"],
        textColor=colors.HexColor("#FF7A59"), fontSize=22, spaceAfter=6,
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        textColor=colors.HexColor("#555555"), fontSize=10, spaceAfter=14,
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Heading2"],
        textColor=colors.HexColor("#111111"), fontSize=13, spaceAfter=6,
    )

    story = []
    story.append(Paragraph("DEIS — Class Intelligence Report", title_style))
    story.append(
        Paragraph(
            f"Generated {datetime.now(timezone.utc).strftime('%b %d, %Y %H:%M UTC')} · "
            f"{overview['total_students']} students · Class avg {overview['class_avg']}% · "
            f"{overview['at_risk_count']} at risk",
            sub_style,
        )
    )

    story.append(Paragraph("Subject averages", h2_style))
    subj_data = [["Subject", "Class avg %"]] + [
        [k, f"{v}%"] for k, v in overview["subject_avg"].items()
    ]
    subj_tbl = Table(subj_data, colWidths=[240, 100])
    subj_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FF7A59")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(subj_tbl)
    story.append(Spacer(1, 18))

    story.append(Paragraph("Student roster", h2_style))
    hdr = ["Student", "Grade", "Avg %", "Risk", "Trend", "Attempts", "Weak topics"]
    data = [hdr]
    for r in rows:
        weak = ", ".join(w["subject"] for w in r["weak_topics"][:3]) or "—"
        data.append(
            [
                r["name"], r["grade"], f"{r['avg_score']}%", r["risk"],
                f"{r['weekly_progress']:+}", str(r["total_attempts"]), weak,
            ]
        )
    tbl = Table(data, colWidths=[110, 55, 50, 50, 50, 55, 170], repeatRows=1)
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111111")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E5E5")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#FAFAFA")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    for idx, r in enumerate(rows, start=1):
        risk_color = (
            colors.HexColor("#EF4444") if r["risk"] == "HIGH"
            else colors.HexColor("#F59E0B") if r["risk"] == "MEDIUM"
            else colors.HexColor("#10B981")
        )
        tbl.setStyle(
            TableStyle(
                [
                    ("TEXTCOLOR", (3, idx), (3, idx), risk_color),
                    ("FONTNAME", (3, idx), (3, idx), "Helvetica-Bold"),
                ]
            )
        )
    story.append(tbl)

    doc.build(story)
    filename = (
        f"deis_class_report_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"
    )
    return Response(
        content=buf.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
