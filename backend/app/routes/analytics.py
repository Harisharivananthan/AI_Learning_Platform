# backend/routers/analytics.py
from fastapi import (
    APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio
import random
import io
import csv
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# Import your app modules correctly
from app.core.database import get_db
from app.crud.metrics_crud import save_metric, get_metric_history
from app.models.metrics import AIMetric

# -----------------------------------------------------------------------------
# Initialize Router
# -----------------------------------------------------------------------------
router = APIRouter(prefix="/analytics", tags=["AI Analytics"])

# Store active websocket connections
active_connections = []

# -----------------------------------------------------------------------------
# 1️⃣ Real-Time WebSocket Metrics Stream
# -----------------------------------------------------------------------------
@router.websocket("/ws/ai-metrics")
async def websocket_ai_metrics(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Simulated AI performance data (replace with real ML logs later)
            data = {
                "timestamp": datetime.now().isoformat(),
                "accuracy": round(random.uniform(0.85, 0.99), 3),
                "loss": round(random.uniform(0.01, 0.15), 3),
                "latency_ms": random.randint(50, 250),
                "users_active": random.randint(10, 300),
                "api_calls_today": random.randint(500, 5000)
            }

            # Save metrics into database
            save_metric(db, {
                "accuracy": data["accuracy"],
                "loss": data["loss"],
                "latency_ms": data["latency_ms"],
                "users_active": data["users_active"],
                "api_calls_today": data["api_calls_today"]
            })

            # Send metrics to all connected clients
            await websocket.send_json(data)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        active_connections.remove(websocket)

# -----------------------------------------------------------------------------
# 2️⃣ Get Metrics History (with optional date range filter)
# -----------------------------------------------------------------------------
@router.get("/history")
def get_metrics_history(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(100, description="Limit number of records"),
    db: Session = Depends(get_db)
):
    query = db.query(AIMetric)

    if start_date and end_date:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            query = query.filter(AIMetric.created_at.between(start, end))
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}

    metrics = query.order_by(AIMetric.created_at.asc()).limit(limit).all()

    return [
        {
            "timestamp": m.created_at,
            "accuracy": m.accuracy,
            "loss": m.loss,
            "latency_ms": m.latency_ms,
            "users_active": m.users_active,
            "api_calls_today": m.api_calls_today
        }
        for m in metrics
    ]

# -----------------------------------------------------------------------------
# 3️⃣ Export Metrics as CSV
# -----------------------------------------------------------------------------
@router.get("/export/csv")
def export_metrics_csv(db: Session = Depends(get_db)):
    metrics = db.query(AIMetric).order_by(AIMetric.created_at.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Accuracy", "Loss", "Latency (ms)", "Users Active", "API Calls"])

    for m in metrics:
        writer.writerow([
            m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            m.accuracy,
            m.loss,
            m.latency_ms,
            m.users_active,
            m.api_calls_today
        ])

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ai_metrics.csv"}
    )

# -----------------------------------------------------------------------------
# 4️⃣ Export Metrics as Excel
# -----------------------------------------------------------------------------
@router.get("/export/excel")
def export_metrics_excel(db: Session = Depends(get_db)):
    metrics = db.query(AIMetric).order_by(AIMetric.created_at.asc()).all()

    data = [
        {
            "Timestamp": m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "Accuracy": m.accuracy,
            "Loss": m.loss,
            "Latency (ms)": m.latency_ms,
            "Users Active": m.users_active,
            "API Calls": m.api_calls_today
        }
        for m in metrics
    ]

    df = pd.DataFrame(data)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="AI Metrics")

    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=ai_metrics.xlsx"}
    )

# -----------------------------------------------------------------------------
# 5️⃣ Export Metrics as PDF
# -----------------------------------------------------------------------------
@router.get("/export/pdf")
def export_metrics_pdf(db: Session = Depends(get_db)):
    metrics = db.query(AIMetric).order_by(AIMetric.created_at.asc()).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = [Paragraph("AI Metrics Report", styles["Title"]), Spacer(1, 12)]

    # Table header
    data = [["Timestamp", "Accuracy", "Loss", "Latency (ms)", "Users Active", "API Calls"]]
    for m in metrics:
        data.append([
            m.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            round(m.accuracy, 3),
            round(m.loss, 3),
            m.latency_ms,
            m.users_active,
            m.api_calls_today
        ])

    table = Table(data)
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=ai_metrics.pdf"}
    )
