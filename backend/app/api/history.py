from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from ..db.session import get_db
from ..db.models import User, EmailSummary
from .auth import require_pro_plan

router = APIRouter(prefix="/history", tags=["history"])


@router.get("/summaries")
async def get_summaries(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    source: Optional[str] = None,
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Get email summary history (PRO only)

    Returns paginated list of past email summaries
    """

    query = db.query(EmailSummary).filter(
        EmailSummary.user_id == current_user.id
    )

    # Filter by source if specified
    if source:
        query = query.filter(EmailSummary.email_source == source)

    # Get total count
    total = query.count()

    # Get summaries
    summaries = query.order_by(
        EmailSummary.created_at.desc()
    ).offset(offset).limit(limit).all()

    results = []
    for summary in summaries:
        results.append({
            "id": summary.id,
            "source": summary.email_source,
            "subject": summary.email_subject,
            "from": summary.email_from,
            "date": summary.email_date.isoformat() if summary.email_date else None,
            "summary": summary.summary,
            "actions": summary.actions,
            "priority": summary.priority_score,
            "created_at": summary.created_at.isoformat()
        })

    return {
        "summaries": results,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/summary/{summary_id}")
async def get_summary(
    summary_id: str,
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Get single summary by ID (PRO only)
    """

    summary = db.query(EmailSummary).filter(
        EmailSummary.id == summary_id,
        EmailSummary.user_id == current_user.id
    ).first()

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    return {
        "id": summary.id,
        "source": summary.email_source,
        "subject": summary.email_subject,
        "from": summary.email_from,
        "date": summary.email_date.isoformat() if summary.email_date else None,
        "summary": summary.summary,
        "actions": summary.actions,
        "priority": summary.priority_score,
        "original_email_id": summary.original_email_id,
        "created_at": summary.created_at.isoformat()
    }


@router.delete("/summary/{summary_id}")
async def delete_summary(
    summary_id: str,
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Delete summary (PRO only)
    """

    summary = db.query(EmailSummary).filter(
        EmailSummary.id == summary_id,
        EmailSummary.user_id == current_user.id
    ).first()

    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")

    db.delete(summary)
    db.commit()

    return {"status": "success", "message": "Summary deleted"}


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics (PRO only)

    Returns stats about user's email summaries
    """

    total_summaries = db.query(EmailSummary).filter(
        EmailSummary.user_id == current_user.id
    ).count()

    # Count by source
    sources = {}
    for source in ['gmail', 'outlook', 'imap', 'manual']:
        count = db.query(EmailSummary).filter(
            EmailSummary.user_id == current_user.id,
            EmailSummary.email_source == source
        ).count()
        if count > 0:
            sources[source] = count

    # Average priority
    from sqlalchemy import func
    avg_priority = db.query(
        func.avg(EmailSummary.priority_score)
    ).filter(
        EmailSummary.user_id == current_user.id
    ).scalar()

    return {
        "total_summaries": total_summaries,
        "by_source": sources,
        "average_priority": round(avg_priority, 2) if avg_priority else 0
    }


@router.delete("/clear")
async def clear_history(
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Clear all history (PRO only)

    Deletes all email summaries for current user
    """

    deleted = db.query(EmailSummary).filter(
        EmailSummary.user_id == current_user.id
    ).delete()

    db.commit()

    return {
        "status": "success",
        "message": f"Deleted {deleted} summaries"
    }
