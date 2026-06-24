"""
SQLAlchemy models for ScamShield AI.

We store every check that's run so we can show a "recent patterns" feed
on the frontend and (later) build simple analytics. No personal data is
required from the user - they just paste text, so we don't store any
identity info, only the message content and the AI's verdict.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ScamCheck(Base):
    """A single scam-check submitted by a user."""

    __tablename__ = "scam_checks"

    id = Column(Integer, primary_key=True, index=True)

    # The raw text the user pasted in (SMS, email, WhatsApp message, etc.)
    message_text = Column(Text, nullable=False)

    # AI's verdict: "safe", "suspicious", or "scam"
    verdict = Column(String(20), nullable=False)

    # 0-100 confidence/risk score for the verdict meter on the frontend
    risk_score = Column(Integer, nullable=False)

    # Category tag, e.g. "phishing", "romance_scam", "fake_job_offer",
    # "lottery_prize", "tech_support_scam", "not_a_scam"
    category = Column(String(50), nullable=False)

    # Short explanation of why - shown to the user as "red flags"
    explanation = Column(Text, nullable=False)

    # Plain-language safety tip / what-to-do-next advice
    advice = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
