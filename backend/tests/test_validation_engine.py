import pytest
from app.services.audit_service import run_validation_checks
from app.schemas.audit import MetricStatus

def test_validation_confidence_threshold():
    metrics = [
        {"name": "Total Revenue", "value": 100000000.0, "confidence_score": 0.95},
        {"name": "Net Income", "value": 20000000.0, "confidence_score": 0.65},  # Low confidence
    ]
    validated, requires_review, avg_conf = run_validation_checks(metrics)
    assert requires_review is True
    assert validated[0]["status"] == MetricStatus.AUTO_VERIFIED.value
    assert validated[1]["status"] == MetricStatus.FLAGGED.value
    assert "below the 85% threshold" in validated[1]["validation_notes"]

def test_validation_balance_sheet_identity():
    # Assets = 100, Liabilities = 80, Equity = 10 (Imbalance: 80+10 = 90 != 100)
    metrics = [
        {"name": "Total Assets", "value": 100000000.0, "confidence_score": 0.95},
        {"name": "Total Liabilities", "value": 80000000.0, "equity": 10000000.0, "confidence_score": 0.95},
    ]
    validated, requires_review, _ = run_validation_checks(metrics)
    assert requires_review is True
    liab = [m for m in validated if m["name"] == "Total Liabilities"][0]
    assert liab["status"] == MetricStatus.FLAGGED.value
    assert "Balance Sheet Imbalance" in liab["validation_notes"]

def test_validation_yoy_anomaly():
    # YoY from 50M to 90M (80% change > 30% threshold)
    metrics = [
        {"name": "Net Income", "value": 90000000.0, "prior_year_value": 50000000.0, "confidence_score": 0.95},
    ]
    validated, requires_review, _ = run_validation_checks(metrics)
    assert requires_review is True
    assert validated[0]["status"] == MetricStatus.FLAGGED.value
    assert "exceeds 30% volatility threshold" in validated[0]["validation_notes"]
