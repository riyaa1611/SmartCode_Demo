"""Seed the database with a sample review and findings for local testing."""
from database import SessionLocal
from models import Review, Finding

def seed():
    db = SessionLocal()
    try:
        # Create sample review
        review = Review(
            repo_name="example/repo",
            pr_number=123,
            pr_url="https://github.com/example/repo/pull/123",
            status="completed"
        )
        db.add(review)
        db.commit()
        db.refresh(review)

        # Create sample findings
        f1 = Finding(
            review_id=review.id,
            category="feature_drift",
            severity="medium",
            description="Feature implementation missing for requirement X",
            file_path="src/module.py",
            line_number=42,
            confidence_score=0.86
        )
        f2 = Finding(
            review_id=review.id,
            category="security",
            severity="high",
            description="Potential SQL injection vulnerability",
            file_path="src/db.py",
            line_number=88,
            confidence_score=0.93
        )
        db.add_all([f1, f2])
        db.commit()
        print(f"Seeded review id={review.id} with 2 findings")
    finally:
        db.close()

if __name__ == '__main__':
    seed()
