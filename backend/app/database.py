"""
SQLite Database Layer for Financial Filing Auditor.
Manages connection, table creation, and queries with zero external service dependencies.
"""
import sqlite3
from datetime import datetime
from typing import List, Optional
from app.core.config import DATABASE_FILE
from app.models.user import User
from app.models.audit import FilingAudit, ExtractedMetricModel
from app.schemas.audit import AuditStatus, MetricStatus


def get_db_connection():
    """
    Returns a configured SQLite connection with row factory.
    """
    conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes database tables for users, audits, and extracted metrics.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        full_name TEXT,
        role TEXT DEFAULT 'auditor',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Filing Audits Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS filing_audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        ticker TEXT NOT NULL,
        year INTEGER NOT NULL,
        filing_type TEXT NOT NULL,
        status TEXT NOT NULL,
        requires_human_review BOOLEAN NOT NULL,
        confidence_overall REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP,
        reviewer_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """)

    # Extracted Metrics Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS extracted_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audit_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        value REAL NOT NULL,
        unit TEXT DEFAULT 'USD',
        confidence_score REAL NOT NULL,
        source_snippet TEXT,
        status TEXT NOT NULL,
        validation_notes TEXT,
        FOREIGN KEY (audit_id) REFERENCES filing_audits (id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()


# Ensure tables are created immediately when database module loads
init_db()


class UserRepository:
    @staticmethod
    def create(email: str, hashed_password: str, full_name: Optional[str] = None, role: str = "auditor") -> User:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, hashed_password, full_name, role) VALUES (?, ?, ?, ?)",
            (email.lower(), hashed_password, full_name, role),
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return User(id=user_id, email=email.lower(), hashed_password=hashed_password, full_name=full_name, role=role)

    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.lower(),))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return User(
            id=row["id"],
            email=row["email"],
            hashed_password=row["hashed_password"],
            full_name=row["full_name"],
            role=row["role"],
            created_at=datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"],
        )

    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return User(
            id=row["id"],
            email=row["email"],
            hashed_password=row["hashed_password"],
            full_name=row["full_name"],
            role=row["role"],
            created_at=datetime.fromisoformat(row["created_at"]) if isinstance(row["created_at"], str) else row["created_at"],
        )


class AuditRepository:
    @staticmethod
    def create_audit(
        user_id: int,
        ticker: str,
        year: int,
        filing_type: str,
        status: str,
        requires_human_review: bool,
        confidence_overall: float,
        metrics: List[dict],
    ) -> FilingAudit:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO filing_audits 
            (user_id, ticker, year, filing_type, status, requires_human_review, confidence_overall) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, ticker.upper(), year, filing_type, status, requires_human_review, confidence_overall),
        )
        audit_id = cursor.lastrowid

        created_metrics = []
        for m in metrics:
            cursor.execute(
                """
                INSERT INTO extracted_metrics 
                (audit_id, name, value, unit, confidence_score, source_snippet, status, validation_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit_id,
                    m["name"],
                    m["value"],
                    m.get("unit", "USD"),
                    m["confidence_score"],
                    m.get("source_snippet"),
                    m.get("status", MetricStatus.AUTO_VERIFIED.value),
                    m.get("validation_notes"),
                ),
            )
            metric_id = cursor.lastrowid
            created_metrics.append(
                ExtractedMetricModel(
                    id=metric_id,
                    audit_id=audit_id,
                    name=m["name"],
                    value=m["value"],
                    unit=m.get("unit", "USD"),
                    confidence_score=m["confidence_score"],
                    source_snippet=m.get("source_snippet"),
                    status=m.get("status", MetricStatus.AUTO_VERIFIED.value),
                    validation_notes=m.get("validation_notes"),
                )
            )

        conn.commit()
        conn.close()

        audit = FilingAudit(
            id=audit_id,
            user_id=user_id,
            ticker=ticker.upper(),
            year=year,
            filing_type=filing_type,
            status=status,
            requires_human_review=requires_human_review,
            confidence_overall=confidence_overall,
        )
        audit.metrics = created_metrics
        return audit

    @staticmethod
    def get_audit(audit_id: int) -> Optional[FilingAudit]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM filing_audits WHERE id = ?", (audit_id,))
        audit_row = cursor.fetchone()
        if not audit_row:
            conn.close()
            return None

        cursor.execute("SELECT * FROM extracted_metrics WHERE audit_id = ?", (audit_id,))
        metric_rows = cursor.fetchall()
        conn.close()

        audit = FilingAudit(
            id=audit_row["id"],
            user_id=audit_row["user_id"],
            ticker=audit_row["ticker"],
            year=audit_row["year"],
            filing_type=audit_row["filing_type"],
            status=audit_row["status"],
            requires_human_review=bool(audit_row["requires_human_review"]),
            confidence_overall=float(audit_row["confidence_overall"]),
            created_at=datetime.fromisoformat(audit_row["created_at"]) if isinstance(audit_row["created_at"], str) else audit_row["created_at"],
            reviewed_at=datetime.fromisoformat(audit_row["reviewed_at"]) if audit_row["reviewed_at"] else None,
            reviewer_id=audit_row["reviewer_id"],
        )
        for r in metric_rows:
            audit.metrics.append(
                ExtractedMetricModel(
                    id=r["id"],
                    audit_id=r["audit_id"],
                    name=r["name"],
                    value=float(r["value"]),
                    unit=r["unit"],
                    confidence_score=float(r["confidence_score"]),
                    source_snippet=r["source_snippet"],
                    status=r["status"],
                    validation_notes=r["validation_notes"],
                )
            )
        return audit

    @staticmethod
    def update_review(
        audit_id: int,
        reviewer_id: int,
        overall_status: str,
        metric_updates: List[dict],
    ) -> Optional[FilingAudit]:
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.utcnow().isoformat()

        cursor.execute(
            """
            UPDATE filing_audits 
            SET status = ?, requires_human_review = 0, reviewed_at = ?, reviewer_id = ?
            WHERE id = ?
            """,
            (overall_status, now, reviewer_id, audit_id),
        )

        for update in metric_updates:
            name = update.get("metric_name")
            corrected = update.get("corrected_value")
            notes = update.get("reviewer_notes")
            if corrected is not None:
                cursor.execute(
                    """
                    UPDATE extracted_metrics 
                    SET value = ?, status = ?, validation_notes = ?
                    WHERE audit_id = ? AND name = ?
                    """,
                    (corrected, MetricStatus.MANUALLY_EDITED.value, notes, audit_id, name),
                )
            elif update.get("decision") == "APPROVE":
                cursor.execute(
                    """
                    UPDATE extracted_metrics 
                    SET status = ?
                    WHERE audit_id = ? AND name = ?
                    """,
                    (MetricStatus.APPROVED.value, audit_id, name),
                )

        conn.commit()
        conn.close()
        return AuditRepository.get_audit(audit_id)

    @staticmethod
    def list_history(limit: int = 50) -> List[FilingAudit]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM filing_audits ORDER BY id DESC LIMIT ?", (limit,))
        ids = [row["id"] for row in cursor.fetchall()]
        conn.close()

        audits = []
        for a_id in ids:
            audit = AuditRepository.get_audit(a_id)
            if audit:
                audits.append(audit)
        return audits
