"""
FilingAudit and ExtractedMetric models for SQLite persistence.
"""
from datetime import datetime
from typing import List, Optional
from app.schemas.audit import AuditStatus, MetricStatus


class ExtractedMetricModel:
    def __init__(
        self,
        id: int,
        audit_id: int,
        name: str,
        value: float,
        unit: str = "USD",
        confidence_score: float = 1.0,
        source_snippet: Optional[str] = None,
        status: str = MetricStatus.AUTO_VERIFIED.value,
        validation_notes: Optional[str] = None,
    ):
        self.id = id
        self.audit_id = audit_id
        self.name = name
        self.value = value
        self.unit = unit
        self.confidence_score = confidence_score
        self.source_snippet = source_snippet
        self.status = status
        self.validation_notes = validation_notes

    def to_dict(self):
        return {
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "confidence_score": self.confidence_score,
            "source_snippet": self.source_snippet,
            "status": self.status,
            "validation_notes": self.validation_notes,
        }


class FilingAudit:
    def __init__(
        self,
        id: int,
        user_id: int,
        ticker: str,
        year: int,
        filing_type: str = "10-K",
        status: str = AuditStatus.PENDING_REVIEW.value,
        requires_human_review: bool = True,
        confidence_overall: float = 0.85,
        created_at: Optional[datetime] = None,
        reviewed_at: Optional[datetime] = None,
        reviewer_id: Optional[int] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.ticker = ticker
        self.year = year
        self.filing_type = filing_type
        self.status = status
        self.requires_human_review = requires_human_review
        self.confidence_overall = confidence_overall
        self.created_at = created_at or datetime.utcnow()
        self.reviewed_at = reviewed_at
        self.reviewer_id = reviewer_id
        self.metrics: List[ExtractedMetricModel] = []

    def to_dict(self):
        return {
            "id": self.id,
            "ticker": self.ticker,
            "year": self.year,
            "filing_type": self.filing_type,
            "status": self.status,
            "requires_human_review": self.requires_human_review,
            "confidence_overall": self.confidence_overall,
            "metrics": [m.to_dict() for m in self.metrics],
            "created_at": self.created_at,
            "reviewed_at": self.reviewed_at,
            "reviewer_id": self.reviewer_id,
        }
