"""
Billing and Account Management Endpoints
Handles subscriptions, payments, and account information.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.responses import APIResponse
from app.models import User
from app.services.stripe_service import stripe_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class SubscriptionPlan(BaseModel):
    """Subscription plan model"""
    plan: str  # free, starter, pro, business, enterprise
    billing_cycle: str = "monthly"  # monthly or yearly


class SubscriptionResponse(BaseModel):
    """Subscription details response"""
    plan: str
    status: str
    current_period_end: int
    renewal_amount: float
    renewal_date: str


class InvoiceResponse(BaseModel):
    """Invoice details response"""
    id: str
    date: int
    amount: float
    status: str
    pdf_url: str


@router.get("/subscription")
async def get_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current subscription details for authenticated user.
    """
    try:
        if not hasattr(user, 'stripe_subscription_id') or not user.stripe_subscription_id:
            return APIResponse.success(
                data={
                    "plan": "free",
                    "status": "active",
                    "quota_monthly": 100,
                    "quota_used": 0,
                    "renewable": False
                },
                message="Free tier subscription"
            )
        
        # Get subscription details from Stripe
        subscription_details = stripe_service.get_subscription_details(
            user.stripe_subscription_id
        )
        
        if not subscription_details:
            raise HTTPException(status_code=500, detail="Could not retrieve subscription")
        
        return APIResponse.success(
            data=subscription_details,
            message="Subscription details retrieved"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving subscription")


@router.post("/subscription/upgrade")
async def upgrade_subscription(
    request: SubscriptionPlan,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upgrade to a new subscription plan.
    """
    try:
        # Validate plan
        valid_plans = ["free", "starter", "pro", "business", "enterprise"]
        if request.plan not in valid_plans:
            raise HTTPException(status_code=400, detail="Invalid plan")
        
        # Update subscription
        success = stripe_service.upgrade_subscription(user, request.plan, db)
        
        if not success:
            raise HTTPException(status_code=500, detail="Could not upgrade subscription")
        
        return APIResponse.success(
            data={"plan": request.plan, "status": "updated"},
            message=f"Successfully upgraded to {request.plan} plan"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error upgrading subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Error upgrading subscription")


@router.post("/subscription/cancel")
async def cancel_subscription(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel current subscription and downgrade to free tier.
    """
    try:
        if not hasattr(user, 'stripe_subscription_id') or not user.stripe_subscription_id:
            raise HTTPException(status_code=400, detail="No active subscription to cancel")
        
        # Cancel subscription
        success = stripe_service.cancel_subscription(user.stripe_subscription_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Could not cancel subscription")
        
        # Downgrade to free tier
        user.plan = "free"
        db.commit()
        
        return APIResponse.success(
            data={"plan": "free", "status": "downgraded"},
            message="Subscription cancelled. Downgraded to free tier."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling subscription: {str(e)}")
        raise HTTPException(status_code=500, detail="Error canceling subscription")


@router.get("/billing/invoices")
async def get_invoices(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get billing invoices for authenticated user.
    """
    try:
        if not hasattr(user, 'stripe_customer_id') or not user.stripe_customer_id:
            return APIResponse.success(
                data=[],
                message="No invoices found"
            )
        
        # Get invoices from Stripe
        invoices = stripe_service.get_invoices(user.stripe_customer_id)
        
        return APIResponse.success(
            data=invoices,
            message=f"Retrieved {len(invoices)} invoices"
        )
        
    except Exception as e:
        logger.error(f"Error getting invoices: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving invoices")


@router.get("/billing/payment-methods")
async def get_payment_methods(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get payment methods for authenticated user.
    """
    try:
        if not hasattr(user, 'stripe_customer_id') or not user.stripe_customer_id:
            return APIResponse.success(
                data=[],
                message="No payment methods found"
            )
        
        # Get payment methods from Stripe
        payment_methods = stripe_service.get_payment_methods(user.stripe_customer_id)
        
        return APIResponse.success(
            data=payment_methods,
            message=f"Retrieved {len(payment_methods)} payment methods"
        )
        
    except Exception as e:
        logger.error(f"Error getting payment methods: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving payment methods")


class PaymentMethodRequest(BaseModel):
    """Payment method request model"""
    payment_method_id: str


@router.post("/billing/payment-methods")
async def add_payment_method(
    request: PaymentMethodRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new payment method for authenticated user.
    """
    try:
        # Ensure Stripe customer exists
        customer_id = stripe_service.create_customer(user, db)
        
        if not customer_id:
            raise HTTPException(status_code=500, detail="Could not create customer")
        
        # Add payment method
        success = stripe_service.add_payment_method(customer_id, request.payment_method_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Could not add payment method")
        
        return APIResponse.success(
            data={"status": "added"},
            message="Payment method added successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding payment method: {str(e)}")
        raise HTTPException(status_code=500, detail="Error adding payment method")


@router.post("/webhooks/stripe")
async def handle_stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    """
    try:
        # Get raw body for signature verification
        body = await request.body()
        
        # Get signature header
        signature = request.headers.get("Stripe-Signature")
        
        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        # Verify and construct event
        import stripe
        try:
            event = stripe.Webhook.construct_event(
                body,
                signature,
                stripe.api_key  # Should be webhook secret in production
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Process webhook
        success = stripe_service.process_webhook(event)
        
        if not success:
            raise HTTPException(status_code=500, detail="Error processing webhook")
        
        return APIResponse.success(
            data={"received": True},
            message="Webhook processed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing webhook")


@router.get("/account/billing-summary")
async def get_billing_summary(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete billing summary for authenticated user.
    """
    try:
        # Get subscription
        plan = getattr(user, 'plan', 'free')
        
        # Get quota info
        from app.services.quota import quota_service
        quota_info = quota_service.get_quota_info(user, db)
        
        # Get billing data if subscribed
        billing_data = {}
        if hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
            invoices = stripe_service.get_invoices(user.stripe_customer_id, limit=3)
            payment_methods = stripe_service.get_payment_methods(user.stripe_customer_id)
            
            billing_data = {
                "invoices": invoices,
                "payment_methods": payment_methods,
                "last_invoice": invoices[0] if invoices else None
            }
        
        return APIResponse.success(
            data={
                "plan": plan,
                "quota_limit": quota_info.get("quota_limit"),
                "quota_used": quota_info.get("quota_used"),
                "quota_remaining": quota_info.get("quota_remaining"),
                "reset_date": quota_info.get("reset_date"),
                "billing": billing_data
            },
            message="Billing summary retrieved"
        )
        
    except Exception as e:
        logger.error(f"Error getting billing summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving billing summary")
