from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid

from ..services.ai import summarize_email, analyze_priority
from ..services.parser import parse_email
from ..utils.validators import sanitize_input
from ..db.session import get_db
from ..db.models import User, EmailSummary
from .auth import get_current_user

router = APIRouter(prefix="/summarize", tags=["summarize"])


class SummarizeRawRequest(BaseModel):
    """Request for summarizing raw email text"""
    text: str
    subject: Optional[str] = None
    from_email: Optional[str] = None
    is_html: bool = False


class SummarizeRawResponse(BaseModel):
    """Response for email summary"""
    summary: str
    actions: List[str]
    priority: int
    key_points: List[str]
    parsed_email: dict


@router.post("/raw", response_model=SummarizeRawResponse)
async def summarize_raw(request: SummarizeRawRequest):
    """
    Summarize raw email text (FREE - no authentication required)

    This endpoint allows free users to paste email text manually
    and get AI summaries without login.
    """

    # Sanitize input
    text = sanitize_input(request.text, max_length=50000)

    if not text or len(text) < 10:
        raise HTTPException(status_code=400, detail="Email text too short")

    # Parse email
    parsed = parse_email(text, is_html=request.is_html)

    # Build metadata
    metadata = {
        'subject': request.subject or parsed.get('subject'),
        'from': request.from_email or parsed.get('from'),
        'date': parsed.get('date')
    }

    # Get AI summary
    email_body = parsed.get('cleaned_body') or parsed.get('body')

    result = await summarize_email(email_body, metadata)

    return {
        "summary": result["summary"],
        "actions": result["actions"],
        "priority": result["priority"],
        "key_points": result["key_points"],
        "parsed_email": {
            "subject": parsed.get("subject"),
            "from": parsed.get("from"),
            "date": parsed.get("date"),
            "has_headers": parsed.get("has_headers"),
            "is_forwarded": parsed.get("is_forwarded")
        }
    }


class SummarizeEmailsRequest(BaseModel):
    """Request for summarizing multiple emails (PRO)"""
    emails: List[dict]  # List of {id, subject, from, body, date}
    source: str  # gmail, outlook, imap


class SummarizeEmailsResponse(BaseModel):
    """Response for multiple email summaries"""
    summaries: List[dict]


@router.post("/emails", response_model=SummarizeEmailsResponse)
async def summarize_emails(
    request: SummarizeEmailsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Summarize multiple emails from integrations (PRO only)

    Requires authentication and PRO plan.
    Stores summaries in database for history.
    """

    # Check PRO plan
    if current_user.plan.value != "pro":
        raise HTTPException(
            status_code=403,
            detail="PRO plan required. Upgrade at /billing/checkout"
        )

    summaries = []

    for email_data in request.emails[:20]:  # Limit to 20 emails
        # Extract email content
        email_body = email_data.get('body', '')
        metadata = {
            'subject': email_data.get('subject'),
            'from': email_data.get('from'),
            'date': email_data.get('date')
        }

        # Get AI summary
        result = await summarize_email(email_body, metadata)

        # Store in database
        summary_record = EmailSummary(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            email_source=request.source,
            email_subject=metadata.get('subject'),
            email_from=metadata.get('from'),
            summary=result['summary'],
            actions=str(result['actions']),
            priority_score=result['priority'],
            original_email_id=email_data.get('id')
        )

        db.add(summary_record)

        summaries.append({
            "id": summary_record.id,
            "email_id": email_data.get('id'),
            "subject": metadata.get('subject'),
            "from": metadata.get('from'),
            "summary": result['summary'],
            "actions": result['actions'],
            "priority": result['priority'],
            "key_points": result['key_points']
        })

    db.commit()

    return {"summaries": summaries}


@router.get("/test")
async def test_summarize():
    """Test endpoint to verify AI service is working"""
    test_email = """
    Subject: Project Update - Q4 Goals

    Hi team,

    I wanted to give you a quick update on our Q4 goals. We've made great progress
    on the customer dashboard, but we need to prioritize the mobile app development.

    Action items:
    - Complete mobile app wireframes by Friday
    - Schedule design review meeting
    - Update project timeline

    Let me know if you have any questions.

    Best,
    John
    """

    result = await summarize_email(test_email)

    return {
        "status": "success",
        "test_result": result
    }
