import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_health_and_root():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_auth_and_audit_lifecycle():
    # 1. Register a test auditor
    unique_email = "auditor_test_suite@firm.com"
    reg_res = client.post("/api/auth/register", json={
        "email": unique_email,
        "password": "Password123!",
        "full_name": "Senior Test Auditor",
    })
    # If user already registered in persistent db, status is 400 or 201
    assert reg_res.status_code in [201, 400]

    # 2. Login
    login_res = client.post("/api/auth/login", json={
        "email": unique_email,
        "password": "Password123!",
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Get /me
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == unique_email

    # 4. Create an audit for MSFT 2023
    audit_res = client.post("/api/audit/create", json={
        "ticker": "MSFT",
        "year": 2023,
        "filing_type": "10-K",
    }, headers=headers)
    assert audit_res.status_code == 201
    audit_data = audit_res.json()
    audit_id = audit_data["id"]
    assert audit_data["ticker"] == "MSFT"
    assert len(audit_data["metrics"]) == 8
    assert audit_data["xbrl_accuracy"] >= 90.0

    # 5. Fetch audit logs (append-only trail)
    logs_res = client.get(f"/api/audit/{audit_id}/logs", headers=headers)
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert len(logs) >= 1
    assert "action" in logs[0]

    # 6. Fetch XBRL reconciliation
    xbrl_res = client.get(f"/api/audit/{audit_id}/xbrl-reconciliation", headers=headers)
    assert xbrl_res.status_code == 200
    xbrl = xbrl_res.json()
    assert xbrl["ticker"] == "MSFT"
    assert "items" in xbrl

    # 7. Submit human review
    review_res = client.post(f"/api/audit/{audit_id}/review", json={
        "overall_decision": "APPROVE",
        "metric_updates": [
            {
                "metric_name": "Net Income",
                "decision": "EDIT",
                "corrected_value": 72400000000.0,
                "reviewer_notes": "Auditor verified footnote adjustment",
            }
        ],
        "comments": "Final audit approval after test verification.",
    }, headers=headers)
    assert review_res.status_code == 200
    updated_audit = review_res.json()
    assert updated_audit["status"] in ["APPROVED", "COMPLETED"]
    assert updated_audit["requires_human_review"] is False

    # 8. Check that new log was appended to audit trail
    logs_res_after = client.get(f"/api/audit/{audit_id}/logs", headers=headers)
    logs_after = logs_res_after.json()
    assert len(logs_after) > len(logs)
    actions = [l["action"] for l in logs_after]
    assert "METRIC_CORRECTED" in actions
    assert "AUDIT_APPROVED" in actions
