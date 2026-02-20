from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.sql import func
from database import Base, engine
from typing import List, Dict, Any

# Choose column types based on the connected database dialect.
# - Postgres: prefer native ARRAY/JSONB for arrays and JSON storage.
# - SQLite (and others): use generic JSON column type.
try:
    dialect_name = engine.dialect.name
except Exception:
    dialect_name = "sqlite"

if dialect_name == "postgresql":
    from sqlalchemy.dialects.postgresql import ARRAY, JSONB
    IssueNumbersType = ARRAY(Integer)
    JSONType = JSONB
else:
    from sqlalchemy import JSON as JSONType
    IssueNumbersType = JSONType


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True, index=True)
    repo_name = Column(String, index=True)
    pr_number = Column(Integer, index=True)
    pr_url = Column(String)
    issue_numbers = Column(IssueNumbersType, nullable=True)
    status = Column(String, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    summary = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0-100 PR confidence
    verdict = Column(String, nullable=True)  # APPROVE / REVIEW_NEEDED / CHANGES_REQUESTED
    score_breakdown = Column(JSONType, nullable=True)  # 5-dimension breakdown
    share_token = Column(String, nullable=True, index=True)
    share_password = Column(String, nullable=True)
    share_expires_at = Column(DateTime(timezone=True), nullable=True)


class Finding(Base):
    __tablename__ = 'findings'

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey('reviews.id'), index=True)
    category = Column(String)  # requirement_drift, security, performance, code_quality, test_gap
    severity = Column(String)  # critical, high, medium, low, info
    title = Column(String, nullable=True)  # Short finding title
    description = Column(Text)
    file_path = Column(String)
    line_number = Column(Integer)
    confidence_score = Column(Float)
    code_snippet = Column(Text, nullable=True)
    suggestion = Column(Text, nullable=True)
    suggested_fix = Column(Text, nullable=True)  # Actionable code fix
    references = Column(JSONType, nullable=True)  # CWE/OWASP/doc links


class ContextCache(Base):
    __tablename__ = 'context_cache'

    id = Column(Integer, primary_key=True, index=True)
    repo_name = Column(String, index=True)
    doc_type = Column(String)  # readme, contributing, architecture
    content = Column(Text)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())