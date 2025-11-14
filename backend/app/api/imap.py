from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
import uuid
from cryptography.fernet import Fernet
import os

from ..services.imap_service import IMAPService, test_imap_connection
from ..db.session import get_db
from ..db.models import User, EmailIntegration
from .auth import require_pro_plan
from ..utils.validators import validate_email, validate_imap_host, validate_port

router = APIRouter(prefix="/imap", tags=["imap"])

# Encryption key
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)


class IMAPConnectRequest(BaseModel):
    """Request to connect IMAP account"""
    host: str
    email: str
    password: str
    port: int = 993
    use_ssl: bool = True


class IMAPListRequest(BaseModel):
    """Request to list IMAP messages"""
    max_results: int = 10
    folder: str = "INBOX"
    unread_only: bool = False


@router.post("/connect")
async def connect_imap(
    request: IMAPConnectRequest,
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Connect IMAP email account (PRO only)

    Test connection and store credentials encrypted
    """

    # Validate inputs
    if not validate_email(request.email):
        raise HTTPException(status_code=400, detail="Invalid email address")

    if not validate_imap_host(request.host):
        raise HTTPException(status_code=400, detail="Invalid IMAP host")

    if not validate_port(request.port):
        raise HTTPException(status_code=400, detail="Invalid port number")

    # Test connection
    connection_test = test_imap_connection(
        request.host,
        request.email,
        request.password,
        request.port
    )

    if not connection_test:
        raise HTTPException(
            status_code=400,
            detail="Failed to connect to IMAP server. Check credentials."
        )

    # Store credentials encrypted
    credentials = {
        'host': request.host,
        'email': request.email,
        'password': request.password,
        'port': request.port,
        'use_ssl': request.use_ssl
    }

    encrypted = cipher_suite.encrypt(json.dumps(credentials).encode())

    # Check if integration already exists
    existing = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'imap'
    ).first()

    if existing:
        # Update existing
        existing.encrypted_credentials = encrypted.decode()
        existing.is_active = True
    else:
        # Create new
        integration = EmailIntegration(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            integration_type='imap',
            encrypted_credentials=encrypted.decode(),
            is_active=True
        )
        db.add(integration)

    db.commit()

    return {
        "status": "success",
        "message": "IMAP account connected successfully"
    }


@router.post("/list")
async def list_imap_messages(
    request: IMAPListRequest,
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    List IMAP messages (PRO only)

    Returns list of messages from IMAP inbox
    """

    # Get user's IMAP integration
    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'imap',
        EmailIntegration.is_active == True
    ).first()

    if not integration:
        raise HTTPException(
            status_code=404,
            detail="IMAP not connected. Please connect your account first."
        )

    # Decrypt credentials
    try:
        decrypted = cipher_suite.decrypt(integration.encrypted_credentials.encode())
        credentials = json.loads(decrypted)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error decrypting credentials")

    # Connect to IMAP
    try:
        imap_service = IMAPService(
            host=credentials['host'],
            email_addr=credentials['email'],
            password=credentials['password'],
            port=credentials['port'],
            use_ssl=credentials.get('use_ssl', True)
        )

        messages = imap_service.list_messages(
            folder=request.folder,
            max_results=request.max_results,
            unread_only=request.unread_only
        )

        imap_service.disconnect()

        return {
            "messages": messages,
            "count": len(messages)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IMAP error: {str(e)}")


@router.get("/folders")
async def get_imap_folders(
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Get list of IMAP folders (PRO only)
    """

    # Get integration
    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'imap',
        EmailIntegration.is_active == True
    ).first()

    if not integration:
        raise HTTPException(status_code=404, detail="IMAP not connected")

    # Decrypt credentials
    try:
        decrypted = cipher_suite.decrypt(integration.encrypted_credentials.encode())
        credentials = json.loads(decrypted)
    except:
        raise HTTPException(status_code=500, detail="Error decrypting credentials")

    # Get folders
    try:
        imap_service = IMAPService(
            host=credentials['host'],
            email_addr=credentials['email'],
            password=credentials['password'],
            port=credentials['port'],
            use_ssl=credentials.get('use_ssl', True)
        )

        folders = imap_service.get_folders()
        imap_service.disconnect()

        return {"folders": folders}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.delete("/disconnect")
async def disconnect_imap(
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Disconnect IMAP integration (PRO only)
    """

    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'imap'
    ).first()

    if integration:
        integration.is_active = False
        db.commit()

    return {"status": "success", "message": "IMAP disconnected"}


@router.get("/status")
async def imap_status(
    current_user: User = Depends(require_pro_plan),
    db: Session = Depends(get_db)
):
    """
    Check IMAP connection status (PRO only)
    """

    integration = db.query(EmailIntegration).filter(
        EmailIntegration.user_id == current_user.id,
        EmailIntegration.integration_type == 'imap',
        EmailIntegration.is_active == True
    ).first()

    connected = integration is not None

    email = None
    if connected:
        try:
            decrypted = cipher_suite.decrypt(integration.encrypted_credentials.encode())
            credentials = json.loads(decrypted)
            email = credentials.get('email')
        except:
            pass

    return {
        "connected": connected,
        "email": email,
        "integration_id": integration.id if integration else None
    }
