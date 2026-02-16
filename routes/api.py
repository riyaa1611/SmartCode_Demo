from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Review, Finding
from typing import List

router = APIRouter()

@router.get("/review/{pr_id}")
async def get_review_status(pr_id: int, db: Session = Depends(get_db)):
    """Retrieve review status by PR ID"""
    review = db.query(Review).filter(Review.id == pr_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Get findings for this review
    findings = db.query(Finding).filter(Finding.review_id == pr_id).all()
    
    return {
        "review": review,
        "findings": findings
    }

@router.post("/analyze")
async def trigger_analysis(pr_url: str, db: Session = Depends(get_db)):
    """Manually trigger analysis for a PR"""
    # TODO: Implement manual analysis trigger
    return {"message": f"Analysis triggered for {pr_url}"}

@router.get("/metrics/{repo}")
async def get_repository_metrics(repo: str, db: Session = Depends(get_db)):
    """Show review stats for repository"""
    # TODO: Implement metrics collection
    reviews = db.query(Review).filter(Review.repo_name == repo).all()
    
    total_reviews = len(reviews)
    completed_reviews = len([r for r in reviews if r.status == "completed"])
    
    return {
        "repository": repo,
        "total_reviews": total_reviews,
        "completed_reviews": completed_reviews,
        "completion_rate": completed_reviews / total_reviews if total_reviews > 0 else 0
    }


@router.get("/demo/review/{pr_id}")
async def demo_review(pr_id: int):
    """Demo endpoint returning a sample review JSON for UI testing."""
    sample = {
        "review": {
            "id": pr_id,
            "repo_name": "example/repo",
            "pr_number": 123,
            "pr_url": "https://github.com/example/repo/pull/123",
            "status": "completed",
            "created_at": "2025-11-24T00:00:00Z",
            "completed_at": "2025-11-24T00:05:00Z",
            "summary": "This is a demo review summary.",
            "share_token": None,
            "share_password": None,
            "share_expires_at": None
        },
        "findings": [
            {
                "id": 1,
                "category": "feature_drift",
                "severity": "medium",
                "description": "Feature implementation missing for requirement X",
                "file_path": "src/module.py",
                "line_number": 42,
                "confidence_score": 0.86,
                "code_snippet": "def feature_x():\n    pass",
                "suggestion": "Implement the feature logic here."
            },
            {
                "id": 2,
                "category": "security",
                "severity": "high",
                "description": "Potential SQL injection vulnerability",
                "file_path": "src/db.py",
                "line_number": 88,
                "confidence_score": 0.93,
                "code_snippet": "query = 'SELECT * FROM users WHERE name = ' + user_input",
                "suggestion": "Use parameterized queries to prevent SQL injection."
            }
        ]
    }
    return sample