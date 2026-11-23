"""
Financial Filing Audit endpoints connected to SQLite persistence and the validation engine.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_user
from app.database import AuditRepository
from app.models.user import User
from app.schemas.audit import (
    AuditCreate,
    AuditResponse,
    AuditStatus,
    HumanReviewPayload,
)
from app.services.audit_service import execute_audit

router = APIRouter(prefix="/audit", tags=["Filing Audit"])


@router.post("/create", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
def create_audit(
    audit_in: AuditCreate, current_user: User = Depends(get_current_user)
):
    """
    Initiates an audit for a ticker and year, executes validation engine, and saves to SQLite.
    """
    audit = execute_audit(
        user_id=current_user.id,
        ticker=audit_in.ticker,
        year=audit_in.year,
        filing_type=audit_in.filing_type,
    )
    return AuditResponse(**audit.to_dict())


@router.get("/sample", response_model=AuditResponse)
def get_sample_audit(current_user: User = Depends(get_current_user)):
    """
    Returns an active sample audit for AAPL 2023.
    """
    history = AuditRepository.list_history(limit=1)
    if history:
        return AuditResponse(**history[0].to_dict())

    # Create a fresh sample audit if table is empty
    sample = execute_audit(
        user_id=current_user.id,
        ticker="AAPL",
        year=2023,
        filing_type="10-K",
    )
    return AuditResponse(**sample.to_dict())


@router.get("/{audit_id}", response_model=AuditResponse)
def get_audit(audit_id: int, current_user: User = Depends(get_current_user)):
    """
    Retrieves an audit and its extracted metrics by ID.
    """
    audit = AuditRepository.get_audit(audit_id)
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit with ID {audit_id} not found.",
        )
    return AuditResponse(**audit.to_dict())


@router.post("/{audit_id}/review", response_model=AuditResponse)
def submit_human_review(
    audit_id: int,
    payload: HumanReviewPayload,
    current_user: User = Depends(get_current_user),
):
    """
    Submits human auditor decisions (APPROVE, EDIT, REJECT) and updates the audit state in SQLite.
    """
    existing = AuditRepository.get_audit(audit_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit with ID {audit_id} not found.",
        )

    status_map = {
        "APPROVE": AuditStatus.APPROVED.value,
        "EDIT": AuditStatus.COMPLETED.value,
        "REJECT": AuditStatus.REJECTED.value,
    }
    target_status = status_map.get(payload.overall_decision.value, AuditStatus.COMPLETED.value)

    updates = [item.model_dump() for item in payload.metric_updates]
    updated_audit = AuditRepository.update_review(
        audit_id=audit_id,
        reviewer_id=current_user.id,
        overall_status=target_status,
        metric_updates=updates,
    )

    return AuditResponse(**updated_audit.to_dict())


@router.get("/history", response_model=List[AuditResponse])
def get_audit_history(current_user: User = Depends(get_current_user)):
    """
    Lists past filings audited and their human review status.
    """
    audits = AuditRepository.list_history(limit=50)
    return [AuditResponse(**a.to_dict()) for a in audits]
