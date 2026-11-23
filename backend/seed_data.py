"""
Demo Data Seeder for Financial Filing Auditor.
Creates demo accounts and pre-loads corporate 10-K filings in various audit states.
"""
import sys
import os

# Add backend directory to sys.path so app imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import UserRepository, AuditRepository, init_db
from app.core.security import hash_password
from app.services.audit_service import execute_audit

def seed():
    print("🌱 Initializing Database Schema...")
    init_db()

    print("👤 Creating Demo Auditor User...")
    auditor_email = "auditor@example.com"
    existing_user = UserRepository.get_by_email(auditor_email)
    if not existing_user:
        user = UserRepository.create(
            email=auditor_email,
            hashed_password=hash_password("Password123!"),
            full_name="Lead Financial Auditor",
            role="senior_auditor"
        )
        print(f"   Created user: {user.email} (Password: Password123!)")
    else:
        user = existing_user
        print(f"   User {user.email} already exists.")

    print("\n📑 Seeding Corporate Financial Filings...")

    # 1. Seed Microsoft 2023 10-K (Approved)
    msft_audit = execute_audit(user_id=user.id, ticker="MSFT", year=2023, filing_type="10-K")
    AuditRepository.update_review(
        audit_id=msft_audit.id,
        reviewer_id=user.id,
        overall_status="APPROVED",
        metric_updates=[{"metric_name": "Net Income", "decision": "APPROVE"}]
    )
    print(f"   [Approved] MSFT 2023 10-K (Audit #{msft_audit.id})")

    # 2. Seed Tesla 2023 10-K (Approved)
    tsla_audit = execute_audit(user_id=user.id, ticker="TSLA", year=2023, filing_type="10-K")
    AuditRepository.update_review(
        audit_id=tsla_audit.id,
        reviewer_id=user.id,
        overall_status="APPROVED",
        metric_updates=[{"metric_name": "Net Income", "decision": "APPROVE"}]
    )
    print(f"   [Approved] TSLA 2023 10-K (Audit #{tsla_audit.id})")

    # 3. Seed Apple 2023 10-K (Pending Human Review with Flagged items)
    aapl_audit = execute_audit(user_id=user.id, ticker="AAPL", year=2023, filing_type="10-K")
    print(f"   [Pending Review] AAPL 2023 10-K (Audit #{aapl_audit.id}) - Flagged for human review")

    print("\n✅ Database seeding completed successfully!")
    print("   Total Audits:", len(AuditRepository.list_history()))
    print("   Auditor Login: auditor@example.com / Password123!")

if __name__ == "__main__":
    seed()
