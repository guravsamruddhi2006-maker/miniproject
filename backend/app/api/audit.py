"""
Financial Filing Audit endpoints connected to SQLite persistence, PDF document intake,
immutable audit logs, and SEC XBRL ground-truth verification.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.responses import JSONResponse
from app.api.deps import get_current_user
from app.database import AuditRepository, AuditLogRepository
from app.models.user import User
from app.schemas.audit import (
    AuditCreate,
    AuditResponse,
    AuditStatus,
    AuditLogResponse,
    HumanReviewPayload,
    XBRLReconciliationResponse,
)
from app.services.audit_service import execute_audit, process_pdf_document_audit
from app.services.xbrl_service import reconcile_metrics_with_xbrl

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


@router.post("/upload-pdf", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf_audit(
    file: UploadFile = File(...),
    ticker: str = Form(...),
    year: int = Form(...),
    filing_type: str = Form("10-K"),
    current_user: User = Depends(get_current_user),
):
    """
    Uploads a corporate PDF filing (Form 10-K/10-Q), extracts financial metrics,
    validates values, reconciles against XBRL facts, and initiates audit.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported document format: Only PDF files (.pdf) are currently supported.",
        )

    file_bytes = await file.read()
    try:
        audit = process_pdf_document_audit(
            user_id=current_user.id,
            file_bytes=file_bytes,
            filename=file.filename,
            ticker=ticker,
            year=year,
            filing_type=filing_type,
        )
        return AuditResponse(**audit.to_dict())
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(val_err),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF document: {str(e)}",
        )


@router.get("/sample", response_model=AuditResponse)
def get_sample_audit(current_user: User = Depends(get_current_user)):
    """
    Returns an active sample audit for AAPL 2023.
    """
    history = AuditRepository.list_history(limit=1)
    if history:
        return AuditResponse(**history[0].to_dict())

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


@router.get("/{audit_id}/logs", response_model=List[AuditLogResponse])
def get_audit_logs(audit_id: int, current_user: User = Depends(get_current_user)):
    """
    Returns the immutable append-only audit trail logs for this filing.
    """
    audit = AuditRepository.get_audit(audit_id)
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit with ID {audit_id} not found.",
        )
    logs = AuditLogRepository.get_logs_for_audit(audit_id)
    return [AuditLogResponse(**l.to_dict()) for l in logs]


@router.get("/{audit_id}/xbrl-reconciliation", response_model=XBRLReconciliationResponse)
def get_xbrl_reconciliation(audit_id: int, current_user: User = Depends(get_current_user)):
    """
    Returns ground-truth reconciliation comparing extracted metrics against official SEC XBRL facts.
    """
    audit = AuditRepository.get_audit(audit_id)
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit with ID {audit_id} not found.",
        )
    metrics_dicts = [m.to_dict() for m in audit.metrics]
    report = reconcile_metrics_with_xbrl(metrics_dicts, audit.ticker, audit.year)
    return XBRLReconciliationResponse(**report)


@router.post("/{audit_id}/review", response_model=AuditResponse)
def submit_human_review(
    audit_id: int,
    payload: HumanReviewPayload,
    current_user: User = Depends(get_current_user),
):
    """
    Submits human auditor decisions (APPROVE, EDIT, REJECT), updates the audit state in SQLite,
    and appends immutable records to the audit trail.
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
        comments=payload.comments,
    )

    return AuditResponse(**updated_audit.to_dict())


@router.get("/history", response_model=List[AuditResponse])
def get_audit_history(current_user: User = Depends(get_current_user)):
    """
    Lists past filings audited and their human review status.
    """
    audits = AuditRepository.list_history(limit=50)
    return [AuditResponse(**a.to_dict()) for a in audits]
