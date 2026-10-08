import hashlib
import sqlite3

from pathlib import Path
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parents[1]

DB_PATH = (
    ROOT / "evaluation" / "reviews" / "certifications.db"
)


def sql_hash(sql):
    """Identify the exact SQL being reviewed."""
    return hashlib.sha256(
        str(sql).strip().encode("utf-8")
    ).hexdigest()


def init_db():
    """Create the database and review table."""

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS certifications (
                version TEXT NOT NULL,
                question_id TEXT NOT NULL,
                sql_hash TEXT NOT NULL,
                decision TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                comments TEXT,
                reviewed_at TEXT NOT NULL,
                PRIMARY KEY (
                    version,
                    question_id,
                    sql_hash
                )
            )
        """)

        conn.commit()

    finally:
        conn.close()


def save_review(
    version,
    question_id,
    generated_sql,
    decision,
    reviewer,
    comments
):
    """Save or update a certification decision."""

    if decision not in ("APPROVED", "REJECTED"):
        raise ValueError("Invalid review decision")

    if not reviewer.strip():
        raise ValueError("Reviewer is required")

    init_db()

    conn = sqlite3.connect(DB_PATH)

    try:
        conn.execute("""
            INSERT INTO certifications (
                version,
                question_id,
                sql_hash,
                decision,
                reviewer,
                comments,
                reviewed_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)

            ON CONFLICT (
                version,
                question_id,
                sql_hash
            )

            DO UPDATE SET
                decision = excluded.decision,
                reviewer = excluded.reviewer,
                comments = excluded.comments,
                reviewed_at = excluded.reviewed_at
        """, (
            str(version),
            str(question_id),
            sql_hash(generated_sql),
            decision,
            reviewer.strip(),
            comments.strip(),
            datetime.now(
                timezone.utc
            ).isoformat(timespec="seconds")
        ))

        conn.commit()

    finally:
        conn.close()


def get_review(
    version,
    question_id,
    generated_sql
):
    """Find the review for this exact generated SQL."""

    init_db()

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        result = conn.execute("""
            SELECT *
            FROM certifications
            WHERE version = ?
              AND question_id = ?
              AND sql_hash = ?
        """, (
            str(version),
            str(question_id),
            sql_hash(generated_sql)
        )).fetchone()

        return dict(result) if result else None

    finally:
        conn.close()
