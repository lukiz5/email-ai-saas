from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional
import os
import httpx
from jose import jwt, JWTError

from ..db.session import get_db
from ..db.models import User, PlanType

router = APIRouter(prefix="/auth", tags=["auth"])

CLERK_PEM_PUBLIC_KEY = os.getenv("CLERK_PEM_PUBLIC_KEY", "")


async def verify_clerk_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verify Clerk JWT token

    Args:
        authorization: Bearer token from header

    Returns:
        Decoded token payload

    Raises:
        HTTPException if token invalid
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        # Decode JWT
        payload = jwt.decode(
            token,
            CLERK_PEM_PUBLIC_KEY,
            algorithms=["RS256"]
        )

        return payload

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


async def get_current_user(
    token_payload: dict = Depends(verify_clerk_token),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user

    Args:
        token_payload: Decoded JWT payload
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException if user not found
    """
    user_id = token_payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Get or create user
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        # Create new user
        email = token_payload.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email required")

        user = User(
            id=user_id,
            email=email,
            plan=PlanType.FREE
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


async def require_pro_plan(current_user: User = Depends(get_current_user)) -> User:
    """
    Require user to have PRO plan

    Args:
        current_user: Current user

    Returns:
        User object

    Raises:
        HTTPException if not PRO user
    """
    if current_user.plan != PlanType.PRO:
        raise HTTPException(
            status_code=403,
            detail="PRO plan required for this feature"
        )

    return current_user


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "plan": current_user.plan.value,
        "created_at": current_user.created_at.isoformat()
    }


@router.get("/verify")
async def verify_token(token_payload: dict = Depends(verify_clerk_token)):
    """Verify token is valid"""
    return {
        "valid": True,
        "user_id": token_payload.get("sub")
    }
