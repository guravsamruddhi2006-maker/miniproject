"""
Audit schemas defining request and response contracts for financial filing extractions and reviews.
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


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


class AuditResponse(BaseModel):
    id: int
    ticker: str
    year: int
    filing_type: str
    status: AuditStatus
    requires_human_review: bool
    confidence_overall: float
    metrics: List[ExtractedMetric] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    reviewed_at: Optional[datetime] = None
    reviewer_id: Optional[int] = None

    class Config:
        from_attributes = True
