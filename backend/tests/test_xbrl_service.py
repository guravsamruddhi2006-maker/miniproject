import pytest
from app.services.xbrl_service import (
    fetch_xbrl_company_facts,
    reconcile_metrics_with_xbrl,
)

def test_fetch_xbrl_company_facts():
    facts = fetch_xbrl_company_facts("AAPL", 2023)
    assert facts is not None
    assert "Total Revenue" in facts
    assert facts["Total Revenue"] == 383285000000.0
    assert facts["Diluted EPS"] == 6.13

def test_reconcile_metrics_with_xbrl():
    extracted = [
        {"name": "Total Revenue", "value": 383285000000.0},
        {"name": "Net Income", "value": 96995000000.0},
        {"name": "Diluted EPS", "value": 6.13},
    ]
    report = reconcile_metrics_with_xbrl(extracted, "AAPL", 2023)
    assert report["ticker"] == "AAPL"
    assert report["overall_accuracy_percentage"] >= 95.0
    assert len(report["items"]) == 3
    for item in report["items"]:
        assert item["verified"] is True
