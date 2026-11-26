"""
FilingAudit, ExtractedMetric, AuditLog, and Document models for SQLite persistence.
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
            "id": self.id,
            "name": self.name,
            "value": self.value,
            "unit": self.unit,
            "confidence_score": self.confidence_score,
            "source_snippet": self.source_snippet,
            "status": self.status,
            "validation_notes": self.validation_notes,
        }


class AuditLogModel:
    def __init__(
        self,
        id: int,
        audit_id: int,
        action: str,
        metric_name: Optional[str] = None,
        previous_value: Optional[float] = None,
        new_value: Optional[float] = None,
        previous_status: Optional[str] = None,
        new_status: Optional[str] = None,
        reviewer_id: Optional[int] = None,
        reviewer_email: Optional[str] = None,
        comments: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.id = id
        self.audit_id = audit_id
        self.metric_name = metric_name
        self.action = action
        self.previous_value = previous_value
        self.new_value = new_value
        self.previous_status = previous_status
        self.new_status = new_status
        self.reviewer_id = reviewer_id
        self.reviewer_email = reviewer_email
        self.comments = comments
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "audit_id": self.audit_id,
            "metric_name": self.metric_name,
            "action": self.action,
            "previous_value": self.previous_value,
            "new_value": self.new_value,
            "previous_status": self.previous_status,
            "new_status": self.new_status,
            "reviewer_id": self.reviewer_id,
            "reviewer_email": self.reviewer_email,
            "comments": self.comments,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
        }


class DocumentModel:
    def __init__(
        self,
        id: int,
        filename: str,
        file_path: str,
        file_size: int,
        mime_type: str = "application/pdf",
        audit_id: Optional[int] = None,
        uploaded_at: Optional[datetime] = None,
    ):
        self.id = id
        self.filename = filename
        self.file_path = file_path
        self.file_size = file_size
        self.mime_type = mime_type
        self.audit_id = audit_id
        self.uploaded_at = uploaded_at or datetime.utcnow()

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "audit_id": self.audit_id,
            "uploaded_at": self.uploaded_at.isoformat() if isinstance(self.uploaded_at, datetime) else self.uploaded_at,
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
        xbrl_accuracy: float = 95.0,
        document_id: Optional[int] = None,
        document_filename: Optional[str] = None,
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
        self.xbrl_accuracy = xbrl_accuracy
        self.document_id = document_id
        self.document_filename = document_filename
        self.created_at = created_at or datetime.utcnow()
        self.reviewed_at = reviewed_at
        self.reviewer_id = reviewer_id
        self.metrics: List[ExtractedMetricModel] = []
        self.logs: List[AuditLogModel] = []

    def to_dict(self):
        return {
            "id": self.id,
            "ticker": self.ticker,
            "year": self.year,
            "filing_type": self.filing_type,
            "status": self.status,
            "requires_human_review": self.requires_human_review,
            "confidence_overall": self.confidence_overall,
            "xbrl_accuracy": self.xbrl_accuracy,
            "document_id": self.document_id,
            "document_filename": self.document_filename,
            "metrics": [m.to_dict() for m in self.metrics],
            "logs": [l.to_dict() for l in self.logs],
            "created_at": self.created_at,
            "reviewed_at": self.reviewed_at,
            "reviewer_id": self.reviewer_id,
        }
