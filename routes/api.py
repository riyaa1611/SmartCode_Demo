from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Review, Finding
from typing import List

router = APIRouter()


@router.get("/review/{pr_id}")
async def get_review_status(pr_id: int, db: Session = Depends(get_db)):
    """Retrieve review status by PR ID."""
    review = db.query(Review).filter(Review.id == pr_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    findings = db.query(Finding).filter(Finding.review_id == pr_id).all()

    return {
        "review": {
            "id": review.id,
            "repo_name": review.repo_name,
            "pr_number": review.pr_number,
            "pr_url": review.pr_url,
            "status": review.status,
            "created_at": review.created_at,
            "completed_at": review.completed_at,
            "summary": review.summary,
            "confidence_score": review.confidence_score,
            "verdict": review.verdict,
            "score_breakdown": review.score_breakdown,
            "share_token": review.share_token,
            "share_password": review.share_password,
            "share_expires_at": review.share_expires_at,
        },
        "findings": [
            {
                "id": f.id,
                "category": f.category,
                "severity": f.severity,
                "title": f.title,
                "description": f.description,
                "file_path": f.file_path,
                "line_number": f.line_number,
                "confidence_score": f.confidence_score,
                "code_snippet": f.code_snippet,
                "suggestion": f.suggestion,
                "suggested_fix": f.suggested_fix,
                "references": f.references,
            }
            for f in findings
        ],
    }


@router.post("/analyze")
async def trigger_analysis(pr_url: str, db: Session = Depends(get_db)):
    """Manually trigger analysis for a PR."""
    return {"message": f"Analysis triggered for {pr_url}"}


@router.get("/metrics/{repo:path}")
async def get_repository_metrics(repo: str, db: Session = Depends(get_db)):
    """Show review stats for a repository."""
    reviews = db.query(Review).filter(Review.repo_name == repo).all()

    total_reviews = len(reviews)
    completed_reviews = len([r for r in reviews if r.status == "completed"])
    avg_confidence = 0.0
    verdict_dist = {"APPROVE": 0, "REVIEW_NEEDED": 0, "CHANGES_REQUESTED": 0}

    if completed_reviews:
        scores = [r.confidence_score for r in reviews if r.confidence_score is not None]
        avg_confidence = sum(scores) / len(scores) if scores else 0
        for r in reviews:
            if r.verdict in verdict_dist:
                verdict_dist[r.verdict] += 1

    return {
        "repository": repo,
        "total_reviews": total_reviews,
        "completed_reviews": completed_reviews,
        "completion_rate": completed_reviews / total_reviews if total_reviews > 0 else 0,
        "average_confidence_score": round(avg_confidence, 1),
        "verdict_distribution": verdict_dist,
    }


@router.get("/review/{review_id}/metrics")
async def get_review_metrics(review_id: int, db: Session = Depends(get_db)):
    """Get computed metrics for a specific review."""
    from analysis_engine.metrics_calculator import MetricsCalculator

    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    findings = db.query(Finding).filter(Finding.review_id == review_id).all()
    findings_dicts = [
        {"severity": f.severity, "category": f.category}
        for f in findings
    ]

    calc = MetricsCalculator()
    bug_risk = calc.calculate_bug_risk(findings_dicts)
    security = calc.calculate_security_index(findings_dicts)
    tech_debt = calc.calculate_tech_debt({
        "cyclomatic_complexity": 0,
        "function_count": 0,
        "nesting_depth": 0,
    })

    return {
        "review_id": review_id,
        "bug_risk": bug_risk,
        "security_severity": security,
        "tech_debt": tech_debt,
        "review_confidence": {
            "score": review.confidence_score,
            "verdict": review.verdict,
        },
    }


@router.get("/demo/review/{pr_id}")
async def demo_review(pr_id: int):
    """Demo endpoint returning a realistic sample review with all fields."""
    sample = {
        "review": {
            "id": pr_id,
            "repo_name": "acme-corp/payment-service",
            "pr_number": 247,
            "pr_url": "https://github.com/acme-corp/payment-service/pull/247",
            "status": "completed",
            "created_at": "2026-02-20T14:30:00Z",
            "completed_at": "2026-02-20T14:32:18Z",
            "summary": (
                "SmartCode AI Review: 4 finding(s). "
                "Confidence: 72/100 (REVIEW_NEEDED). "
                "Overall score: 74/100."
            ),
            "confidence_score": 72,
            "verdict": "REVIEW_NEEDED",
            "score_breakdown": {
                "requirement_alignment": 85,
                "security_safety": 58,
                "code_quality": 70,
                "test_coverage_signal": 45,
                "static_analysis_clean": 82,
            },
            "share_token": None,
            "share_password": None,
            "share_expires_at": None,
        },
        "findings": [
            {
                "id": 1,
                "category": "security",
                "severity": "critical",
                "title": "SQL Injection in payment query handler",
                "description": (
                    "The get_payment_history() function concatenates user input "
                    "directly into a SQL query string without parameterization, "
                    "allowing an attacker to execute arbitrary SQL."
                ),
                "file_path": "src/payments/queries.py",
                "line_number": 42,
                "confidence_score": 0.95,
                "code_snippet": 'query = f"SELECT * FROM payments WHERE user_id = \'{user_id}\'"',
                "suggestion": "Use parameterized queries to prevent SQL injection.",
                "suggested_fix": (
                    'cursor.execute("SELECT * FROM payments WHERE user_id = %s", (user_id,))'
                ),
                "references": ["CWE-89", "OWASP A03:2021 - Injection"],
            },
            {
                "id": 2,
                "category": "requirement_drift",
                "severity": "high",
                "title": "Missing pagination for transaction listing",
                "description": (
                    "Issue #189 requires paginated transaction listing with "
                    "limit/offset support. The current implementation returns "
                    "all records with no pagination, which will cause performance "
                    "issues at scale."
                ),
                "file_path": "src/payments/routes.py",
                "line_number": 67,
                "confidence_score": 0.88,
                "code_snippet": "transactions = db.query(Transaction).filter_by(user_id=uid).all()",
                "suggestion": "Add limit/offset parameters to the query.",
                "suggested_fix": (
                    "transactions = db.query(Transaction)"
                    ".filter_by(user_id=uid)"
                    ".offset(offset).limit(limit).all()"
                ),
                "references": ["Issue #189 — Requirement: Paginated transaction listing"],
            },
            {
                "id": 3,
                "category": "performance",
                "severity": "medium",
                "title": "N+1 query in payment detail enrichment",
                "description": (
                    "Inside the for loop at line 91, a separate database query "
                    "fetches merchant details for each payment. With 1000 payments, "
                    "this produces 1001 queries instead of 2."
                ),
                "file_path": "src/payments/service.py",
                "line_number": 91,
                "confidence_score": 0.82,
                "code_snippet": (
                    "for payment in payments:\n"
                    "    merchant = db.query(Merchant).get(payment.merchant_id)"
                ),
                "suggestion": "Use a JOIN or prefetch merchants in a single query.",
                "suggested_fix": (
                    "merchant_ids = [p.merchant_id for p in payments]\n"
                    "merchants = {m.id: m for m in db.query(Merchant)"
                    ".filter(Merchant.id.in_(merchant_ids)).all()}"
                ),
                "references": [],
            },
            {
                "id": 4,
                "category": "code_quality",
                "severity": "low",
                "title": "Missing error handling for external API call",
                "description": (
                    "The call to the payment gateway API at line 128 has no "
                    "try/except or timeout, which could cause unhandled "
                    "exceptions and request hangs in production."
                ),
                "file_path": "src/payments/gateway.py",
                "line_number": 128,
                "confidence_score": 0.76,
                "code_snippet": "response = requests.post(gateway_url, json=payload)",
                "suggestion": "Add timeout and error handling.",
                "suggested_fix": (
                    "try:\n"
                    "    response = requests.post(gateway_url, json=payload, timeout=10)\n"
                    "    response.raise_for_status()\n"
                    "except requests.RequestException as e:\n"
                    "    logger.error(f'Gateway error: {e}')\n"
                    "    raise PaymentGatewayError(str(e))"
                ),
                "references": [],
            },
        ],
    }
    return sample