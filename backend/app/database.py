"""
SQLite Database Layer for Financial Filing Auditor.
Manages connection, table creation, append-only audit trail logs, document storage, and queries.
Includes connection reuse and 30s lock timeout to prevent SQLite concurrency deadlocks.
"""
import sqlite3
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from app.core.config import DATABASE_FILE
from app.models.user import User
from app.models.audit import FilingAudit, ExtractedMetricModel, AuditLogModel, DocumentModel
from app.schemas.audit import AuditStatus, MetricStatus


def get_db_connection(timeout: float = 30.0):
    """
    Returns a configured SQLite connection with row factory and timeout.
    """
    conn = sqlite3.connect(DATABASE_FILE, timeout=timeout, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Initializes database tables for users, audits, extracted metrics, documents, and append-only audit logs.
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

    # Documents Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audit_id INTEGER,
        filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        mime_type TEXT DEFAULT 'application/pdf',
        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        xbrl_accuracy REAL DEFAULT 95.0,
        document_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP,
        reviewer_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (document_id) REFERENCES documents (id)
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

    # Append-Only Audit Logs Table (Immutable Decision Trail)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        audit_id INTEGER NOT NULL,
        metric_name TEXT,
        action TEXT NOT NULL,
        previous_value REAL,
        new_value REAL,
        previous_status TEXT,
        new_status TEXT,
        reviewer_id INTEGER,
        reviewer_email TEXT,
        comments TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (audit_id) REFERENCES filing_audits (id) ON DELETE CASCADE
    )
    """)

    # Safely migrate columns if existing table lacked document_id or xbrl_accuracy
    try:
        cursor.execute("ALTER TABLE filing_audits ADD COLUMN xbrl_accuracy REAL DEFAULT 95.0")
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE filing_audits ADD COLUMN document_id INTEGER")
    except Exception:
        pass

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


class DocumentRepository:
    @staticmethod
    def create_document(
        filename: str,
        file_path: str,
        file_size: int,
        mime_type: str = "application/pdf",
        audit_id: Optional[int] = None,
    ) -> DocumentModel:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO documents (filename, file_path, file_size, mime_type, audit_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (filename, file_path, file_size, mime_type, audit_id),
        )
        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return DocumentModel(
            id=doc_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            mime_type=mime_type,
            audit_id=audit_id,
        )

    @staticmethod
    def get_document(doc_id: int) -> Optional[DocumentModel]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return DocumentModel(
            id=row["id"],
            filename=row["filename"],
            file_path=row["file_path"],
            file_size=row["file_size"],
            mime_type=row["mime_type"],
            audit_id=row["audit_id"],
            uploaded_at=datetime.fromisoformat(row["uploaded_at"]) if isinstance(row["uploaded_at"], str) else row["uploaded_at"],
        )


class AuditLogRepository:
    @staticmethod
    def append_log(
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
        conn: Optional[sqlite3.Connection] = None,
    ) -> AuditLogModel:
        should_close = False
        if conn is None:
            conn = get_db_connection()
            should_close = True

        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO audit_logs 
            (audit_id, metric_name, action, previous_value, new_value, previous_status, new_status, reviewer_id, reviewer_email, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                audit_id,
                metric_name,
                action,
                previous_value,
                new_value,
                previous_status,
                new_status,
                reviewer_id,
                reviewer_email,
                comments,
            ),
        )
        log_id = cursor.lastrowid
        if should_close:
            conn.commit()
            conn.close()

        return AuditLogModel(
            id=log_id,
            audit_id=audit_id,
            action=action,
            metric_name=metric_name,
            previous_value=previous_value,
            new_value=new_value,
            previous_status=previous_status,
            new_status=new_status,
            reviewer_id=reviewer_id,
            reviewer_email=reviewer_email,
            comments=comments,
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def get_logs_for_audit(audit_id: int) -> List[AuditLogModel]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs WHERE audit_id = ? ORDER BY id ASC", (audit_id,))
        rows = cursor.fetchall()
        conn.close()

        logs = []
        for r in rows:
            logs.append(
                AuditLogModel(
                    id=r["id"],
                    audit_id=r["audit_id"],
                    action=r["action"],
                    metric_name=r["metric_name"],
                    previous_value=float(r["previous_value"]) if r["previous_value"] is not None else None,
                    new_value=float(r["new_value"]) if r["new_value"] is not None else None,
                    previous_status=r["previous_status"],
                    new_status=r["new_status"],
                    reviewer_id=r["reviewer_id"],
                    reviewer_email=r["reviewer_email"],
                    comments=r["comments"],
                    created_at=datetime.fromisoformat(r["created_at"]) if isinstance(r["created_at"], str) else r["created_at"],
                )
            )
        return logs


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
        document_id: Optional[int] = None,
        xbrl_accuracy: float = 95.0,
    ) -> FilingAudit:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO filing_audits 
            (user_id, ticker, year, filing_type, status, requires_human_review, confidence_overall, xbrl_accuracy, document_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, ticker.upper(), year, filing_type, status, requires_human_review, confidence_overall, xbrl_accuracy, document_id),
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

        # Append initial immutable audit log using the same connection before commit
        user = UserRepository.get_by_id(user_id)
        action_name = "AUDIT_PAUSED_FOR_REVIEW" if requires_human_review else "AUDIT_AUTO_APPROVED"
        AuditLogRepository.append_log(
            audit_id=audit_id,
            action=action_name,
            reviewer_id=user_id,
            reviewer_email=user.email if user else "system@agent",
            comments=f"Automated filing intake and validation completed with confidence {confidence_overall * 100:.0f}%.",
            conn=conn,
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
            xbrl_accuracy=xbrl_accuracy,
            document_id=document_id,
        )
        audit.metrics = created_metrics
        audit.logs = AuditLogRepository.get_logs_for_audit(audit_id)
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

        doc_filename = None
        doc_id = audit_row["document_id"] if "document_id" in audit_row.keys() else None
        if doc_id:
            cursor.execute("SELECT filename FROM documents WHERE id = ?", (doc_id,))
            doc_row = cursor.fetchone()
            if doc_row:
                doc_filename = doc_row["filename"]

        conn.close()

        xbrl_acc = float(audit_row["xbrl_accuracy"]) if "xbrl_accuracy" in audit_row.keys() and audit_row["xbrl_accuracy"] is not None else 95.0

        audit = FilingAudit(
            id=audit_row["id"],
            user_id=audit_row["user_id"],
            ticker=audit_row["ticker"],
            year=audit_row["year"],
            filing_type=audit_row["filing_type"],
            status=audit_row["status"],
            requires_human_review=bool(audit_row["requires_human_review"]),
            confidence_overall=float(audit_row["confidence_overall"]),
            xbrl_accuracy=xbrl_acc,
            document_id=doc_id,
            document_filename=doc_filename,
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
        audit.logs = AuditLogRepository.get_logs_for_audit(audit_id)
        return audit

    @staticmethod
    def update_review(
        audit_id: int,
        reviewer_id: int,
        overall_status: str,
        metric_updates: List[dict],
        comments: Optional[str] = None,
    ) -> Optional[FilingAudit]:
        existing = AuditRepository.get_audit(audit_id)
        if not existing:
            return None

        user = UserRepository.get_by_id(reviewer_id)
        reviewer_email = user.email if user else "auditor@demo.com"

        metric_dict = {m.name: m for m in existing.metrics}
        conn = get_db_connection()
        cursor = conn.cursor()
        now = datetime.now(timezone.utc).isoformat()

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
            orig_m = metric_dict.get(name)

            if corrected is not None and orig_m:
                cursor.execute(
                    """
                    UPDATE extracted_metrics 
                    SET value = ?, status = ?, validation_notes = ?
                    WHERE audit_id = ? AND name = ?
                    """,
                    (corrected, MetricStatus.MANUALLY_EDITED.value, notes, audit_id, name),
                )
                AuditLogRepository.append_log(
                    audit_id=audit_id,
                    action="METRIC_CORRECTED",
                    metric_name=name,
                    previous_value=orig_m.value,
                    new_value=float(corrected),
                    previous_status=orig_m.status,
                    new_status=MetricStatus.MANUALLY_EDITED.value,
                    reviewer_id=reviewer_id,
                    reviewer_email=reviewer_email,
                    comments=notes or f"Manual override for {name}",
                    conn=conn,
                )
            elif update.get("decision") == "APPROVE" and orig_m:
                cursor.execute(
                    """
                    UPDATE extracted_metrics 
                    SET status = ?
                    WHERE audit_id = ? AND name = ?
                    """,
                    (MetricStatus.APPROVED.value, audit_id, name),
                )
                AuditLogRepository.append_log(
                    audit_id=audit_id,
                    action="METRIC_APPROVED",
                    metric_name=name,
                    previous_value=orig_m.value,
                    new_value=orig_m.value,
                    previous_status=orig_m.status,
                    new_status=MetricStatus.APPROVED.value,
                    reviewer_id=reviewer_id,
                    reviewer_email=reviewer_email,
                    comments="Metric verified against filing evidence.",
                    conn=conn,
                )

        # Log overall audit decision
        AuditLogRepository.append_log(
            audit_id=audit_id,
            action=f"AUDIT_{overall_status}",
            previous_status=existing.status,
            new_status=overall_status,
            reviewer_id=reviewer_id,
            reviewer_email=reviewer_email,
            comments=comments or f"Overall filing decision marked as {overall_status}.",
            conn=conn,
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
