"""Update the database schema to add new columns for SmartCode v2.

Run this script to add:
  - Review: confidence_score, verdict, score_breakdown
  - Finding: title, suggested_fix, references
"""
import sqlite3
import os

DB_PATH = os.getenv("DEV_DB_PATH", os.path.join(os.path.dirname(__file__), "dev.db"))


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ── Review table additions ──
    review_columns = {
        "confidence_score": "REAL",
        "verdict": "VARCHAR",
        "score_breakdown": "TEXT",  # JSON stored as text in SQLite
    }
    for col, dtype in review_columns.items():
        try:
            cursor.execute(f"ALTER TABLE reviews ADD COLUMN {col} {dtype}")
            print(f"  ✓ Added reviews.{col}")
        except sqlite3.OperationalError:
            print(f"  – reviews.{col} already exists")

    # ── Finding table additions ──
    finding_columns = {
        "title": "VARCHAR",
        "suggested_fix": "TEXT",
        "references": "TEXT",  # JSON stored as text in SQLite
    }
    for col, dtype in finding_columns.items():
        try:
            cursor.execute(f"ALTER TABLE findings ADD COLUMN {col} {dtype}")
            print(f"  ✓ Added findings.{col}")
        except sqlite3.OperationalError:
            print(f"  – findings.{col} already exists")

    conn.commit()
    conn.close()
    print("\nSchema migration complete.")


if __name__ == "__main__":
    print(f"Migrating database: {DB_PATH}\n")
    migrate()
