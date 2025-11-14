import os
import stripe
from typing import Dict, Any

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class BillingService:
    """Stripe billing service"""

    PRICE_ID_PRO = os.getenv("STRIPE_PRICE_ID_PRO", "price_XXXXXX")  # Set in env
    SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "http://localhost:5173/success")
    CANCEL_URL = os.getenv("STRIPE_CANCEL_URL", "http://localhost:5173/pricing")

    @staticmethod
    def create_customer(email: str, user_id: str) -> str:
        """
        Create Stripe customer

        Args:
            email: Customer email
            user_id: Internal user ID

        Returns:
            Stripe customer ID
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={'user_id': user_id}
            )
            return customer.id

        except stripe.error.StripeError as e:
            print(f"Error creating customer: {e}")
            return None

    @staticmethod
    def create_checkout_session(customer_id: str, user_id: str) -> Dict[str, Any]:
        """
        Create Stripe Checkout session for PRO subscription

        Args:
            customer_id: Stripe customer ID
            user_id: Internal user ID

        Returns:
            Dictionary with checkout session URL
        """
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=['card'],
                line_items=[{
                    'price': BillingService.PRICE_ID_PRO,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=BillingService.SUCCESS_URL + '?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=BillingService.CANCEL_URL,
                metadata={'user_id': user_id}
            )

            return {
                'url': session.url,
                'session_id': session.id
            }

        except stripe.error.StripeError as e:
            print(f"Error creating checkout session: {e}")
            return None

    @staticmethod
    def create_portal_session(customer_id: str) -> str:
        """
        Create Stripe Customer Portal session

        Args:
            customer_id: Stripe customer ID

        Returns:
            Portal URL
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=os.getenv("STRIPE_RETURN_URL", "http://localhost:5173/settings")
            )

            return session.url

        except stripe.error.StripeError as e:
            print(f"Error creating portal session: {e}")
            return None

    @staticmethod
    def get_subscription(subscription_id: str) -> Dict[str, Any]:
        """
        Get subscription details

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            Subscription data
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)

            return {
                'id': subscription.id,
                'status': subscription.status,
                'current_period_end': subscription.current_period_end,
                'cancel_at_period_end': subscription.cancel_at_period_end
            }

        except stripe.error.StripeError as e:
            print(f"Error getting subscription: {e}")
            return None

    @staticmethod
    def cancel_subscription(subscription_id: str) -> bool:
        """
        Cancel subscription

        Args:
            subscription_id: Stripe subscription ID

        Returns:
            True if successful
        """
        try:
            stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return True

        except stripe.error.StripeError as e:
            print(f"Error canceling subscription: {e}")
            return False

    @staticmethod
    def verify_webhook_signature(payload: bytes, signature: str) -> bool:
        """
        Verify Stripe webhook signature

        Args:
            payload: Request body
            signature: Stripe signature header

        Returns:
            True if valid
        """
        webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

        try:
            stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            return True

        except stripe.error.SignatureVerificationError:
            return False

    @staticmethod
    def handle_webhook_event(event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Stripe webhook event

        Args:
            event: Stripe event object

        Returns:
            Dictionary with action to take
        """
        event_type = event['type']

        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            return {
                'action': 'activate_subscription',
                'customer_id': session['customer'],
                'subscription_id': session['subscription'],
                'user_id': session['metadata'].get('user_id')
            }

        elif event_type == 'customer.subscription.deleted':
            subscription = event['data']['object']
            return {
                'action': 'deactivate_subscription',
                'customer_id': subscription['customer'],
                'subscription_id': subscription['id']
            }

        elif event_type == 'customer.subscription.updated':
            subscription = event['data']['object']
            return {
                'action': 'update_subscription',
                'customer_id': subscription['customer'],
                'subscription_id': subscription['id'],
                'status': subscription['status']
            }

        return {'action': 'ignore'}
