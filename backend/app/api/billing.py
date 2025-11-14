from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from ..services.billing_service import BillingService
from ..db.session import get_db
from ..db.models import User, PlanType
from .auth import get_current_user

router = APIRouter(prefix="/billing", tags=["billing"])


class CheckoutSessionResponse(BaseModel):
    """Checkout session response"""
    url: str
    session_id: str


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create Stripe Checkout session for PRO subscription

    Creates or retrieves Stripe customer and returns checkout URL
    """

    # Create or get Stripe customer
    if not current_user.stripe_customer_id:
        customer_id = BillingService.create_customer(
            email=current_user.email,
            user_id=current_user.id
        )

        if not customer_id:
            raise HTTPException(status_code=500, detail="Failed to create customer")

        current_user.stripe_customer_id = customer_id
        db.commit()
    else:
        customer_id = current_user.stripe_customer_id

    # Create checkout session
    session = BillingService.create_checkout_session(
        customer_id=customer_id,
        user_id=current_user.id
    )

    if not session:
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

    return {
        "url": session['url'],
        "session_id": session['session_id']
    }


@router.post("/portal")
async def create_portal_session(
    current_user: User = Depends(get_current_user)
):
    """
    Create Stripe Customer Portal session

    Allows users to manage their subscription
    """

    if not current_user.stripe_customer_id:
        raise HTTPException(status_code=404, detail="No subscription found")

    portal_url = BillingService.create_portal_session(
        customer_id=current_user.stripe_customer_id
    )

    if not portal_url:
        raise HTTPException(status_code=500, detail="Failed to create portal session")

    return {"url": portal_url}


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events

    Processes subscription events and updates user plan
    """

    # Get raw body
    body = await request.body()

    # Verify signature
    if not BillingService.verify_webhook_signature(body, stripe_signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Parse event
    import json
    event = json.loads(body)

    # Handle event
    action = BillingService.handle_webhook_event(event)

    if action['action'] == 'activate_subscription':
        # Activate PRO plan
        user_id = action.get('user_id')
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.plan = PlanType.PRO
                user.stripe_subscription_id = action['subscription_id']
                db.commit()

    elif action['action'] == 'deactivate_subscription':
        # Deactivate PRO plan
        customer_id = action['customer_id']
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            user.plan = PlanType.FREE
            user.stripe_subscription_id = None
            db.commit()

    elif action['action'] == 'update_subscription':
        # Update subscription status
        customer_id = action['customer_id']
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            status = action['status']
            if status == 'active':
                user.plan = PlanType.PRO
            elif status in ['canceled', 'unpaid', 'past_due']:
                user.plan = PlanType.FREE
            db.commit()

    return {"status": "success"}


@router.get("/subscription")
async def get_subscription(
    current_user: User = Depends(get_current_user)
):
    """
    Get current subscription details

    Returns user's plan and subscription status
    """

    result = {
        "plan": current_user.plan.value,
        "has_subscription": current_user.stripe_subscription_id is not None
    }

    if current_user.stripe_subscription_id:
        subscription = BillingService.get_subscription(
            current_user.stripe_subscription_id
        )

        if subscription:
            result.update({
                "status": subscription['status'],
                "current_period_end": subscription['current_period_end'],
                "cancel_at_period_end": subscription['cancel_at_period_end']
            })

    return result


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel subscription (at period end)

    Cancels user's PRO subscription
    """

    if not current_user.stripe_subscription_id:
        raise HTTPException(status_code=404, detail="No active subscription")

    success = BillingService.cancel_subscription(
        current_user.stripe_subscription_id
    )

    if not success:
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")

    return {
        "status": "success",
        "message": "Subscription will be canceled at period end"
    }


@router.get("/pricing")
async def get_pricing():
    """
    Get pricing information

    Returns pricing details for FREE and PRO plans
    """

    return {
        "plans": [
            {
                "name": "FREE",
                "price": 0,
                "interval": "forever",
                "features": [
                    "Manual email input",
                    "AI summaries",
                    "Action extraction",
                    "Priority scoring",
                    "Browser-only storage"
                ]
            },
            {
                "name": "PRO",
                "price": 9.99,
                "interval": "month",
                "features": [
                    "Everything in FREE",
                    "Gmail integration",
                    "Outlook integration",
                    "IMAP support",
                    "Smart replies",
                    "Cloud history",
                    "Unlimited usage",
                    "Priority support"
                ]
            }
        ]
    }
