from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import json
import uuid
from cryptography.fernet import Fernet
import os

from ..services.outlook_service import OutlookService, get_outlook_oauth_url, exchange_code_for_token
from ..db.session import get_db
from ..db.models import User, EmailIntegration
from .auth import require_pro_plan

router = APIRouter(prefix="/outlook", tags=["outlook"])

# Encryption key
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)


class OutlookAuthResponse(BaseModel):
    """Outlook OAuth URL response"""
    auth_url: str


class OutlookCallbackRequest(BaseModel):
    """Outlook OAuth callback"""
    code: str
    user_id: str


class OutlookListRequest(BaseModel):
    """Request to list Outlook messages"""
    max_results: int = 10
    folder: str = "inbox"


@router.get("/auth", response_model=OutlookAuthResponse)
async def outlook_auth(current_user: User = Depends(require_pro_plan)):
    """
    Get Outlook OAuth URL (PRO only)

    Returns URL to redirect user for Microsoft authorization
    """
    auth_url = get_outlook_oauth_url()

    return {"auth_url": auth_url}


@router.post("/callback")
async def outlook_callback(
    request: OutlookCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Handle Outlook OAuth callback

    Exchange authorization code for access token
    """

    try:
        # Exchange code for token
        token_result = await exchange_code_for_token(request.code)

        if 'error' in token_result:
            raise HTTPException(
                status_code=400,
                detail=f"OAuth error: {token_result.get('error_description')}"
            )

        # Store tokens
        credentials = {
            'access_token': token_result['access_token'],
            'refresh_token': token_result.get('refresh_token'),
            'expires_in': token_result.get('expires_in')
        }

        # Encrypt credentials
        encrypted = cipher_suite.encrypt(json.dumps(credentials).encode())

        # Store integration
        integration = EmailIntegration(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            integration_type='outlook',
            encrypted_credentials=encrypted.decode(),
            is_active=True
        )

        db.add(integration)
        db.commit()

        return {
            "status": "success",
            "message": "Outlook connected successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/list")
async def list_outlook_messages(
    request: OutlookListRequest,
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    List Outlook messages (PRO only)

    Returns list of messages from user's Outlook inbox
    """

    # Get user's Outlook integration
    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'outlook',
        EmailIntegration.is_active == True
    ).first()

    if not integration:
        raise HTTPException(
            status_code=404,
            detail="Outlook not connected. Please connect your account first."
        )

    # Decrypt credentials
    try:
        decrypted = cipher_suite.decrypt(integration.encrypted_credentials.encode())
        credentials = json.loads(decrypted)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error decrypting credentials")

    # Initialize Outlook service
    try:
        outlook_service = OutlookService(credentials['access_token'])
        messages = await outlook_service.list_messages(
            max_results=request.max_results,
            folder=request.folder
        )

        return {
            "messages": messages,
            "count": len(messages)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outlook API error: {str(e)}")


@router.get("/message/{message_id}")
async def get_outlook_message(
    message_id: str,
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Get single Outlook message (PRO only)
    """

    # Get integration
    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'outlook',
        EmailIntegration.is_active == True
    ).first()

    if not integration:
        raise HTTPException(status_code=404, detail="Outlook not connected")

    # Decrypt credentials
    try:
        decrypted = cipher_suite.decrypt(integration.encrypted_credentials.encode())
        credentials = json.loads(decrypted)
    except:
        raise HTTPException(status_code=500, detail="Error decrypting credentials")

    # Get message
    try:
        outlook_service = OutlookService(credentials['access_token'])
        message = await outlook_service.get_message(message_id)

        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        return message

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/disconnect")
async def disconnect_outlook(
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Disconnect Outlook integration (PRO only)
    """

    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'outlook'
    ).first()

    if integration:
        integration.is_active = False
        db.commit()

    return {"status": "success", "message": "Outlook disconnected"}


@router.get("/status")
async def outlook_status(
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Check Outlook connection status (PRO only)
    """

    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'outlook',
        EmailIntegration.is_active == True
    ).first()

    return {
        "connected": integration is not None,
        "integration_id": integration.id if integration else None
    }
