from fastapi import APIRouter, Request, Header, HTTPException, Depends
import hashlib
import hmac
import json
from config import settings
from database import get_db
from models import Review
from worker import analyze_pull_request
import os

router = APIRouter()

def verify_signature(payload_body, secret_token, signature_header):
    """Verify that the payload was sent from GitHub by validating SHA256.
    
    Args:
        payload_body: original request body to verify (bytes)
        secret_token: GitHub webhook secret token (str)
        signature_header: header received from GitHub (str)
    """
    if not signature_header:
        raise HTTPException(status_code=400, detail="Missing X-Hub-Signature-256 header")
        
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=401, detail="Request signatures didn't match!")

@router.post("/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    db = Depends(get_db)
):
    # Get the payload
    payload_body = await request.body()
    
    # Verify the signature
    verify_signature(payload_body, settings.github_webhook_secret, x_hub_signature_256)
    
    # Parse the event
    event_data = json.loads(payload_body.decode('utf-8'))
    event_type = request.headers.get("X-GitHub-Event")
    
    if event_type == "pull_request":
        action = event_data.get("action")
        if action in ["opened", "synchronize"]:
            # Process PR
            await process_pull_request(event_data, db)
    elif event_type == "issue_comment":
        action = event_data.get("action")
        if action == "created":
            # Process comment
            await process_issue_comment(event_data, db)
    
    return {"status": "success"}

async def process_pull_request(event_data, db):
    """Process pull request events"""
    pr = event_data.get("pull_request")
    pr_number = pr.get("number")
    repo_full_name = pr.get("base", {}).get("repo", {}).get("full_name")
    installation_id = event_data.get("installation", {}).get("id")
    
    # Create or update review record
    review = Review(
        repo_name=repo_full_name,
        pr_number=pr_number,
        pr_url=pr.get("html_url"),
        status="pending"
    )
    
    db.add(review)
    db.commit()
    db.refresh(review)
    
    # Queue analysis task
    analyze_pull_request.delay(repo_full_name, pr_number, installation_id)
    print(f"Queued analysis for PR #{pr_number} in {repo_full_name}")

async def process_issue_comment(event_data, db):
    """Process issue comment events"""
    # TODO: Implement comment processing
    print("Processing issue comment")