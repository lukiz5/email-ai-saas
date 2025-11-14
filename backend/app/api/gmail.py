from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List
import json
import uuid
from cryptography.fernet import Fernet
import os

from ..services.gmail_service import GmailService, get_gmail_oauth_url
from ..db.session import get_db
from ..db.models import User, EmailIntegration
from .auth import require_pro_plan

router = APIRouter(prefix="/gmail", tags=["gmail"])

# Encryption key for storing tokens
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)


class GmailAuthResponse(BaseModel):
    """Gmail OAuth URL response"""
    auth_url: str


class GmailCallbackRequest(BaseModel):
    """Gmail OAuth callback"""
    code: str
    user_id: str


class GmailListRequest(BaseModel):
    """Request to list Gmail messages"""
    max_results: int = 10
    query: Optional[str] = ""


@router.get("/auth", response_model=GmailAuthResponse)
async def gmail_auth(current_user: User = Depends(require_pro_plan)):
    """
    Get Gmail OAuth URL (PRO only)

    Returns URL to redirect user for Gmail authorization
    """
    auth_url = get_gmail_oauth_url()

    return {"auth_url": auth_url}


@router.post("/callback")
async def gmail_callback(
    request: GmailCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Handle Gmail OAuth callback

    Exchange authorization code for tokens and store encrypted
    """

    # This is a simplified version - in production, you'd exchange the code
    # for access token using google_auth_oauthlib

    # For now, we'll create a placeholder
    credentials = {
        'token': 'placeholder_access_token',
        'refresh_token': 'placeholder_refresh_token',
        'token_uri': 'https://oauth2.googleapis.com/token'
    }

    # Encrypt credentials
    encrypted = cipher_suite.encrypt(json.dumps(credentials).encode())

    # Store integration
    integration = EmailIntegration(
        id=str(uuid.uuid4()),
        user_id=request.user_id,
        integration_type='gmail',
        encrypted_credentials=encrypted.decode(),
        is_active=True
    )

    db.add(integration)
    db.commit()

    return {
        "status": "success",
        "message": "Gmail connected successfully"
    }


@router.post("/list")
async def list_gmail_messages(
    request: GmailListRequest,
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    List Gmail messages (PRO only)

    Returns list of messages from user's Gmail inbox
    """

    # Get user's Gmail integration
    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'gmail',
        EmailIntegration.is_active == True
    ).first()

    if not integration:
        raise HTTPException(
            status_code=404,
            detail="Gmail not connected. Please connect your account first."
        )

    # Decrypt credentials
    try:
        decrypted = cipher_suite.decrypt(integration.encrypted_credentials.encode())
        credentials = json.loads(decrypted)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error decrypting credentials")

    # Initialize Gmail service
    try:
        gmail_service = GmailService(credentials)
        messages = gmail_service.list_messages(
            max_results=request.max_results,
            query=request.query
        )

        return {
            "messages": messages,
            "count": len(messages)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gmail API error: {str(e)}")


@router.get("/message/{message_id}")
async def get_gmail_message(
    message_id: str,
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Get single Gmail message (PRO only)
    """

    # Get integration
    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'gmail',
        EmailIntegration.is_active == True
    ).first()

    if not integration:
        raise HTTPException(status_code=404, detail="Gmail not connected")

    # Decrypt credentials
    try:
        decrypted = cipher_suite.decrypt(integration.encrypted_credentials.encode())
        credentials = json.loads(decrypted)
    except:
        raise HTTPException(status_code=500, detail="Error decrypting credentials")

    # Get message
    try:
        gmail_service = GmailService(credentials)
        message = gmail_service.get_message(message_id)

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        return message

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/disconnect")
async def disconnect_gmail(
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Disconnect Gmail integration (PRO only)
    """

    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'gmail'
    ).first()

    if integration:
        integration.is_active = False
        db.commit()

    return {"status": "success", "message": "Gmail disconnected"}


@router.get("/status")
async def gmail_status(
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Check Gmail connection status (PRO only)
    """

    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'gmail',
        EmailIntegration.is_active == True
    ).first()

    return {
        "connected": integration is not None,
        "integration_id": integration.id if integration else None
    }
