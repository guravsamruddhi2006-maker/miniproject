"""
Audit schemas defining request and response contracts for financial filing extractions and reviews.
Includes append-only audit trail logs and SEC XBRL ground-truth reconciliation models.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AuditStatus(str, Enum):
    PENDING_REVIEW = "PENDING_REVIEW"
    FLAGGED = "FLAGGED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    COMPLETED = "COMPLETED"


class MetricStatus(str, Enum):
    AUTO_VERIFIED = "AUTO_VERIFIED"
    FLAGGED = "FLAGGED"
    MANUALLY_EDITED = "MANUALLY_EDITED"
    APPROVED = "APPROVED"


class ExtractedMetric(BaseModel):
    id: Optional[int] = None
    name: str = Field(..., description="e.g. Total Revenue, Net Income, Total Assets")
    value: float = Field(..., description="Numerical value parsed from the filing")
    unit: str = Field(default="USD", description="Currency or unit")
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="AI confidence score between 0.0 and 1.0"
    )
    source_snippet: Optional[str] = Field(
        default=None, description="Exact text or table snippet from the filing"
    )
    status: MetricStatus = Field(
        default=MetricStatus.AUTO_VERIFIED, description="Current metric review status"
    )
    validation_notes: Optional[str] = Field(
        default=None, description="Rule-based validation flags or notes"
    )


class AuditCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker e.g. AAPL")
    year: int = Field(..., ge=2000, le=2030, description="Filing year e.g. 2023")
    filing_type: str = Field(default="10-K", description="Document type e.g. 10-K or 10-Q")


class HumanReviewDecision(str, Enum):
    APPROVE = "APPROVE"
    EDIT = "EDIT"
    REJECT = "REJECT"


class MetricReviewItem(BaseModel):
    metric_name: str
    decision: HumanReviewDecision
    corrected_value: Optional[float] = None
    reviewer_notes: Optional[str] = None


class HumanReviewPayload(BaseModel):
    overall_decision: HumanReviewDecision
    metric_updates: List[MetricReviewItem] = Field(default_factory=list)
    comments: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    audit_id: int
    action: str
    metric_name: Optional[str] = None
    previous_value: Optional[float] = None
    new_value: Optional[float] = None
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    reviewer_id: Optional[int] = None
    reviewer_email: Optional[str] = None
    comments: Optional[str] = None
    created_at: Optional[str] = None


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_size: int
    mime_type: str
    uploaded_at: Optional[str] = None


class XBRLReconciliationItem(BaseModel):
    metric_name: str
    extracted_value: float
    xbrl_value: Optional[float] = None
    difference: float = 0.0
    percentage_diff: float = 0.0
    status: str
    verified: bool


class XBRLReconciliationResponse(BaseModel):
    ticker: str
    year: int
    overall_accuracy_percentage: float
    total_metrics_compared: int
    items: List[XBRLReconciliationItem] = Field(default_factory=list)


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    year: int
    filing_type: str
    status: AuditStatus
    requires_human_review: bool
    confidence_overall: float
    xbrl_accuracy: float = 95.0
    document_id: Optional[int] = None
    document_filename: Optional[str] = None
    metrics: List[ExtractedMetric] = Field(default_factory=list)
    logs: List[AuditLogResponse] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[int] = None
