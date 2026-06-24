"""
ScamShield AI - FastAPI backend.

Detection runs fully offline using a local Machine Learning + NLP
pipeline (see classifier.py) - no external AI API, no API key, no
cost. A TF-IDF + Logistic Regression model (trained on a built-in
scam/safe dataset) estimates risk, and a rule-based NLP layer detects
specific, explainable red flags (urgency language, money requests,
suspicious links, impersonation, etc.) and tags the scam category.

Core endpoint: POST /api/analyze
Takes a pasted message (SMS / email / WhatsApp / DM text) and returns:
  - verdict: safe | suspicious | scam
  - risk_score: 0-100
  - category: scam type tag
  - explanation: red flags found
  - advice: what to do next
"""

from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel

from database import init_db, get_db
from models import ScamCheck
from classifier import analyze_message

app = FastAPI(title="ScamShield AI - Fraud & Scam Detection Tool", version="1.0.0")

# Allow same-origin requests (frontend is now served from this same app),
# kept permissive in case you ever split deployment again later.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create DB tables on startup.
init_db()

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


class AnalyzeRequest(BaseModel):
    message_text: str


class AnalyzeResponse(BaseModel):
    id: int
    verdict: str
    risk_score: int
    category: str
    explanation: str
    advice: str


@app.get("/api/health")
def health_check():
    """Simple endpoint to confirm the API is running."""
    return {"status": "ok", "service": "ScamShield AI - Scam & Fraud Detection Tool"}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest, db: Session = Depends(get_db)):
    """Run the message through the ML + NLP fraud detection engine and store the result."""
    text = payload.message_text.strip()

    if not text:
        raise HTTPException(status_code=400, detail="Message text cannot be empty.")
    if len(text) > 4000:
        raise HTTPException(status_code=400, detail="Message is too long (max 4000 characters).")

    result = analyze_message(text)

    check = ScamCheck(
        message_text=text,
        verdict=result["verdict"],
        risk_score=result["risk_score"],
        category=result["category"],
        explanation=result["explanation"],
        advice=result["advice"],
    )
    db.add(check)
    db.commit()
    db.refresh(check)

    return AnalyzeResponse(
        id=check.id,
        verdict=check.verdict,
        risk_score=check.risk_score,
        category=check.category,
        explanation=check.explanation,
        advice=check.advice,
    )


@app.get("/api/recent")
def recent_checks(limit: int = 8, db: Session = Depends(get_db)):
    """Return the most recent checks (no message text included, for privacy)."""
    checks = (
        db.query(ScamCheck)
        .order_by(desc(ScamCheck.created_at))
        .limit(limit)
        .all()
    )
    return [
        {
            "id": c.id,
            "verdict": c.verdict,
            "risk_score": c.risk_score,
            "category": c.category,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in checks
    ]


@app.get("/api/stats")
def stats(db: Session = Depends(get_db)):
    """Simple aggregate stats for the 'community impact' counter on the frontend."""
    total = db.query(ScamCheck).count()
    scams_caught = db.query(ScamCheck).filter(ScamCheck.verdict == "scam").count()
    return {"total_checks": total, "scams_caught": scams_caught}


# ---------------------------------------------------------------------------
# Serve the frontend (single-platform deployment - same app, same URL).
# Defined last so it never shadows the /api/* routes above.
# ---------------------------------------------------------------------------

@app.get("/")
def serve_frontend():
    """Serve the one-page app's index.html at the root URL."""
    return FileResponse(FRONTEND_DIR / "index.html")


# Serve styles.css, app.js, and any other static assets directly.
app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
